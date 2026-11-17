#!/usr/bin/env python3
"""Genera la pantalla de apertura (splash) de GeoPre.

La pantalla de apertura que trae Capacitor es el logo de Capacitor sobre
fondo BLANCO: ese es el destello blanco al abrir la app. Se sustituye por
el libro Atlas sobre el color de la marca (#567692), el mismo fondo que
tiene el WebView (backgroundColor en capacitor.config.json), asi que al
abrir la app no hay ningun destello: todo es el mismo color.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = Path("/home/hatch/workspace/your_files/iconos-geopre/media-generation-geopre-icono-2-atlas-0-6d869bc8-ce75-42fd-857d-9a0468538762.webp")
BRAND = (0x56, 0x76, 0x92)

# Splash por orientacion y densidad (tamano en px), igual que los que trae Capacitor.
SPLASHES = {
    "drawable": (480, 320),
    "drawable-port-mdpi": (320, 480),
    "drawable-port-hdpi": (480, 800),
    "drawable-port-xhdpi": (720, 1280),
    "drawable-port-xxhdpi": (960, 1600),
    "drawable-port-xxxhdpi": (1280, 1920),
    "drawable-land-mdpi": (480, 320),
    "drawable-land-hdpi": (800, 480),
    "drawable-land-xhdpi": (1280, 720),
    "drawable-land-xxhdpi": (1600, 960),
    "drawable-land-xxxhdpi": (1920, 1280),
}


def full_bleed_icon():
    """El Atlas con las esquinas rellenadas de color marca (igual que el icono).

    OJO: el blanco de las esquinas esta en regiones desconectadas (el tile
    toca los bordes), asi que hay que sembrar la inundacion en las CUATRO
    esquinas, no solo en (0,0); si no, quedan triangulos blancos.
    """
    from collections import deque
    src = Image.open(SRC).convert("RGBA")
    w, h = src.size
    px = src.load()

    def is_white(p):
        return p[0] > 248 and p[1] > 248 and p[2] > 248 and p[3] > 200

    seen = set()
    for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        if seed in seen or not is_white(px[seed]):
            continue
        q = deque([seed])
        seen.add(seed)
        while q:
            x, y = q.popleft()
            px[x, y] = BRAND + (255,)
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen and is_white(px[nx, ny]):
                    seen.add((nx, ny))
                    q.append((nx, ny))
    out = src.resize((int(w * 1.18), int(h * 1.18)), Image.LANCZOS)
    left = (out.width - w) // 2
    top = (out.height - h) // 2
    return out.crop((left, top, left + w, top + h)).convert("RGB")


def main():
    icon = full_bleed_icon()
    res = ROOT / "android/app/src/main/res"
    for folder, (w, h) in SPLASHES.items():
        canvas = Image.new("RGB", (w, h), BRAND)
        size = int(min(w, h) * 0.55)
        small = icon.resize((size, size), Image.LANCZOS)
        canvas.paste(small, ((w - size) // 2, (h - size) // 2))
        canvas.save(res / folder / "splash.png")
        print(f"{folder}: {w}x{h} icono {size}px")
    print("Splash regenerado: libro Atlas sobre #567692 en todas las densidades.")


if __name__ == "__main__":
    main()
