#!/usr/bin/env python3
"""Icono plano de GeoPre, dibujado por codigo (sin IA).

El libro en acuarela se sigue viendo generado por IA. Este icono es
geometria plana y limpia: un globo terraqueo sobre un libro abierto,
colores planos, sin degradados ni textura. Asi se ve como un icono
disenado, no como una ilustracion.
"""
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path("/tmp/icono-geopre-plano.png")
SIZE = 1024
BG = (0x56, 0x76, 0x92)        # azul pizarra de la marca
CREAM = (0xF7, 0xF1, 0xE3)     # paginas
TERRA = (0xC9, 0x62, 0x3A)     # terracota
DARK = (0x24, 0x34, 0x47)      # contorno azul noche
GLOBE = (0xA8, 0xC8, 0xE0)     # azul claro del globo
LINE = (0x7A, 0x8C, 0xA0)      # lineas de texto


def main():
    img = Image.new("RGB", (SIZE, SIZE), BG)
    d = ImageDraw.Draw(img)
    # Fondo con esquinas redondeadas (el icono es un cuadrado redondeado).
    d.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=230, fill=BG)

    # --- Globo terraqueo (arriba) ---
    cx, cy, r = 512, 360, 165
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GLOBE, outline=DARK, width=14)
    # Meridianos: dos elipses verticales y el ecuador.
    d.ellipse([cx - 70, cy - r + 8, cx + 70, cy + r - 8], outline=DARK, width=7)
    d.ellipse([cx - r + 8, cy - 55, cx + r - 8, cy + 55], outline=DARK, width=7)
    d.line([cx - r + 14, cy, cx + r - 14, cy], fill=DARK, width=7)
    # Tierra: mancha terracota simple (un continente).
    d.ellipse([cx - 95, cy - 70, cx - 5, cy + 10], fill=TERRA)
    d.ellipse([cx - 20, cy + 5, cx + 75, cy + 85], fill=TERRA)

    # --- Libro abierto (abajo) ---
    # Cubierta terracota (silueta de libro abierto).
    cover = [(180, 600), (512, 690), (844, 600), (844, 800), (512, 890), (180, 800)]
    d.polygon(cover, fill=TERRA, outline=DARK, width=10)
    # Paginas crema, un poco mas pequenas.
    pages = [(210, 624), (512, 702), (814, 624), (814, 780), (512, 858), (210, 780)]
    d.polygon(pages, fill=CREAM, outline=DARK, width=8)
    # Pliegue central.
    d.line([512, 702, 512, 858], fill=DARK, width=8)
    # Lineas de texto en cada pagina.
    for y in (700, 730, 760):
        d.line([250, y, 460, y + 14], fill=LINE, width=7)
        d.line([564, y + 14, 774, y], fill=LINE, width=7)

    img.save(OUT)
    print("icono plano en", OUT)


if __name__ == "__main__":
    main()
