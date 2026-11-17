#!/usr/bin/env python3
"""Genera el icono de GeoPre a partir de la geometria real del mapa.

Dibuja el mapamundi en proyeccion Equal Earth (la misma del mapa
interactivo de la app y del mapa ONU 2026) con los poligonos de
Natural Earth 110m de world.ts: tierra en gris claro mate, mar en
azul pizarra apagado y Cuba destacada en terracota. Todo plano,
sin brillos ni aspecto de IA.

Uso: python3 scripts/make-icon.py [ruta/a/world.ts]
Salida: assets/res/mipmap-*/ic_launcher*.png y el foreground
adaptativo, copiados tambien a android/app/src/main/res/.
"""
import json
import math
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
WORLD_TS = Path(
    sys.argv[1]
    if len(sys.argv) > 1
    else "/home/hatch/workspace/ts-spaces/app-de-geografia-para-preuniversitario/client/src/world.ts"
)

SLATE = (62, 74, 86, 255)        # azul pizarra apagado (fondo / mar)
LAND = (221, 226, 229, 255)      # gris claro mate (tierra)
CUBA = (182, 90, 56, 255)        # terracota apagado (Cuba)
RAD = math.pi / 180
SQRT3_2 = math.sqrt(3) / 2
A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796


def equal_earth(lon, lat):
    lam = lon * RAD
    l = math.asin(SQRT3_2 * math.sin(lat * RAD))
    l2 = l * l
    l6 = l2 * l2 * l2
    x = (lam * math.cos(l)) / (SQRT3_2 * (A1 + 3 * A2 * l2 + l6 * (7 * A3 + 9 * A4 * l2)))
    y = -l * (A1 + A2 * l2 + l6 * (A3 + A4 * l2))
    return x, y


def load_world():
    text = WORLD_TS.read_text(encoding="utf-8")
    m = re.search(r"export const WORLD[^=]*=\s*(\[.*\]);?\s*$", text, re.S)
    if not m:
        raise SystemExit("no se encontro el arreglo WORLD en world.ts")
    return json.loads(m.group(1))


def split_ring(flat):
    """Parte un anillo en tramos cuando cruza el antimeridiano."""
    pts = [(flat[i], flat[i + 1]) for i in range(0, len(flat) - 1, 2)]
    out, cur = [], []
    for i, p in enumerate(pts):
        if i and abs(p[0] - pts[i - 1][0]) > 180:
            if len(cur) > 2:
                out.append(cur)
            cur = []
        cur.append(p)
    if len(cur) > 2:
        out.append(cur)
    return out


def project(countries):
    """Proyecta todos los paises; devuelve (tramos, bounds).

    La Antartida queda fuera del icono: en Equal Earth se estira
    como una franja fina en el borde inferior y a tamano de icono
    se lee como un rayajo, no como un continente.
    """
    spans = []  # (nombre, [(x, y), ...])
    xs, ys = [], []
    for c in countries:
        if c["continent"] == "Antártida":
            continue
        for ring in c["polys"]:
            for seg in split_ring(ring):
                proj = [equal_earth(lon, lat) for lon, lat in seg]
                spans.append((c["name"], proj))
                xs.extend(p[0] for p in proj)
                ys.extend(p[1] for p in proj)
    return spans, (min(xs), max(xs), min(ys), max(ys))


def render(spans, bounds, size, shape, bg):
    """Dibuja el mapa en un lienzo cuadrado.

    shape: 'square' (fondo redondeado) o 'round' (circulo) o 'naked'
    (sin fondo, solo tierra, para el foreground adaptativo).
    """
    S = size * 4  # sobremuestreo para bordes suaves
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if shape == "square":
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=bg)
    elif shape == "round":
        d.ellipse([0, 0, S - 1, S - 1], fill=bg)
    x0, x1, y0, y1 = bounds
    # Margen del 6% y centrado; en 'naked' el arte ocupa la zona segura.
    pad = 0.06 if shape != "naked" else 0.20
    scale = min((1 - 2 * pad) * S / (x1 - x0), (1 - 2 * pad) * S / (y1 - y0))
    ox = (S - (x1 - x0) * scale) / 2
    oy = (S - (y1 - y0) * scale) / 2

    def px(p):
        return (ox + (p[0] - x0) * scale, oy + (p[1] - y0) * scale)

    for name, proj in spans:
        color = CUBA if name == "Cuba" else LAND
        d.polygon([px(p) for p in proj], fill=color)
    # Cuba otra vez encima, por si algun pais la tapa en el borde.
    cuba_pts = []
    for name, proj in spans:
        if name == "Cuba":
            d.polygon([px(p) for p in proj], fill=CUBA)
            cuba_pts.extend(proj)
    # Cuba es una franja fina a esta escala y su terracota no se
    # veria: se marca con un punto solido en su centro, que a tamano
    # de icono se lee como "aqui esta Cuba".
    if cuba_pts:
        cx = sum(p[0] for p in cuba_pts) / len(cuba_pts)
        cy = sum(p[1] for p in cuba_pts) / len(cuba_pts)
        ccx, ccy = px((cx, cy))
        r = S * 0.028
        d.ellipse([ccx - r, ccy - r, ccx + r, ccy + r], fill=CUBA)
    return img.resize((size, size), Image.LANCZOS)


def main():
    countries = load_world()
    spans, bounds = project(countries)
    print(f"paises: {len(countries)}, tramos: {len(spans)}")
    sizes = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
    for dest_root in (ROOT / "assets" / "res", ROOT / "android" / "app" / "src" / "main" / "res"):
        for dpi, size in sizes.items():
            folder = dest_root / f"mipmap-{dpi}"
            folder.mkdir(parents=True, exist_ok=True)
            render(spans, bounds, size, "square", SLATE).save(folder / "ic_launcher.png")
            render(spans, bounds, size, "round", SLATE).save(folder / "ic_launcher_round.png")
        folder = dest_root / "mipmap-anydpi-v26"
        folder.mkdir(parents=True, exist_ok=True)
        render(spans, bounds, 432, "naked", SLATE).save(folder / "ic_launcher_foreground.png")
    # Fondo del icono adaptativo: pizarra, a juego con el fondo del icono.
    values = ROOT / "android" / "app" / "src" / "main" / "res" / "values" / "ic_launcher_background.xml"
    values.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
        '    <color name="ic_launcher_background">#3E4A56</color>\n</resources>\n',
        encoding="utf-8",
    )
    print("icono GeoPre generado en assets/res y android res.")


if __name__ == "__main__":
    main()
