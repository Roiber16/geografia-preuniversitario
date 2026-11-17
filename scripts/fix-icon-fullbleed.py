#!/usr/bin/env python3
"""Regenera el icono Atlas de GeoPre como foreground adaptativo FULL-BLEED.

Problema: el foreground anterior tenia las esquinas transparentes
(tile redondeado sobre fondo transparente). MIUI al aplicar su mascara
y escalar el foreground lo renderizaba como una mancha naranja borrosa
(Cuba terracota dominando) en vez del libro.

Solucion: el foreground 432x432 es ahora completamente opaco: fondo
#567692 hasta los bordes, sin transparencia, con el libro mas grande
y centrado. Los iconos legacy y redondos se regeneran de la misma
fuente para que todo sea coherente.
"""
from pathlib import Path
from PIL import Image, ImageDraw

SRC = Path("/home/hatch/workspace/your_files/iconos-geopre/media-generation-geopre-icono-2-atlas-0-6d869bc8-ce75-42fd-857d-9a0468538762.webp")
ROOT = Path("/home/hatch/workspace/geografia-apk")
BG = (0x56, 0x76, 0x92, 255)  # #567692 azul pizarra

def flood_fill_corners(img, fill):
    """Rellena el blanco de las esquinas con el color de fondo."""
    img = img.convert("RGBA")
    w, h = img.size
    px = img.load()
    # El blanco de las esquinas es (255,255,255); las paginas son crema.
    def is_white(p):
        return p[0] > 248 and p[1] > 248 and p[2] > 248 and p[3] > 200
    from collections import deque
    seen = set()
    for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        if seed in seen or not is_white(px[seed]):
            continue
        q = deque([seed])
        seen.add(seed)
        while q:
            x, y = q.popleft()
            px[x, y] = fill
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen and is_white(px[nx, ny]):
                    seen.add((nx, ny))
                    q.append((nx, ny))
    return img

def main():
    src = Image.open(SRC)
    print("fuente:", src.size, src.mode)
    base = flood_fill_corners(src, BG)
    # Comprobar que no queda transparencia ni blanco en las esquinas.
    px = base.load()
    w, h = base.size
    assert px[0, 0] == BG and px[w - 1, h - 1] == BG, "esquinas no rellenadas"
    # Libro mas grande: escalar 1.18x y recortar al centro (solo se
    # recorta fondo, el libro tiene margen).
    big = base.resize((int(w * 1.18), int(h * 1.18)), Image.LANCZOS)
    left = (big.width - w) // 2
    top = (big.height - h) // 2
    full = big.crop((left, top, left + w, top + h))
    # Foreground adaptativo full-bleed 432x432, opaco.
    fg = full.resize((432, 432), Image.LANCZOS).convert("RGBA")
    assert all(p[3] == 255 for p in list(fg.getdata())[::997]), "foreground con transparencia"
    sizes = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
    # Foreground adaptativo (108dp) por densidad: el sistema prefiere la
    # densidad exacta a anydpi, asi que cada densidad lleva el Atlas.
    fg_sizes = {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}
    for dest_root in (ROOT / "assets" / "res", ROOT / "android" / "app" / "src" / "main" / "res"):
        for dpi, size in sizes.items():
            folder = dest_root / f"mipmap-{dpi}"
            folder.mkdir(parents=True, exist_ok=True)
            # Legacy: cuadrado con esquinas redondeadas.
            sq = full.resize((size * 4, size * 4), Image.LANCZOS)
            mask = Image.new("L", sq.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle([0, 0, sq.width - 1, sq.height - 1], radius=int(sq.width * 0.22), fill=255)
            out = Image.new("RGBA", sq.size, (0, 0, 0, 0))
            out.paste(sq, (0, 0), mask)
            out.resize((size, size), Image.LANCZOS).save(folder / "ic_launcher.png")
            # Redondo: circulo.
            mask2 = Image.new("L", sq.size, 0)
            ImageDraw.Draw(mask2).ellipse([0, 0, sq.width - 1, sq.height - 1], fill=255)
            out2 = Image.new("RGBA", sq.size, (0, 0, 0, 0))
            out2.paste(sq, (0, 0), mask2)
            out2.resize((size, size), Image.LANCZOS).save(folder / "ic_launcher_round.png")
            # Foreground adaptativo por densidad (tapa al viejo de Capacitor).
            full.resize((fg_sizes[dpi], fg_sizes[dpi]), Image.LANCZOS).convert("RGBA").save(folder / "ic_launcher_foreground.png")
        folder = dest_root / "mipmap-anydpi-v26"
        folder.mkdir(parents=True, exist_ok=True)
        fg.save(folder / "ic_launcher_foreground.png")
    # Vista previa: como se veria en el launcher a 96px con mascara squircle.
    prev = fg.resize((96, 96), Image.LANCZOS)
    m = Image.new("L", (96, 96), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 95, 95], radius=22, fill=255)
    p = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
    p.paste(prev, (0, 0), m)
    p.save("/tmp/icono-v7-vista-previa.png")
    print("icono regenerado: foreground full-bleed opaco, libro ampliado, preview en /tmp/icono-v7-vista-previa.png")

if __name__ == "__main__":
    main()
