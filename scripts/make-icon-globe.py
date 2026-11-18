#!/usr/bin/env python3
"""Icono plano de GeoPre v3: un globo terraqueo (esfera).

Roi pidio una esfera, o sea un globo terraqueo. Sin meridianos (eso
parecia un atomo) y sin textura de IA: un circulo azul vivo con
continentes verdes y un casquete polar crema, sobre fondo terracota
vivo. Todo plano, dibujado por codigo, con colores.
"""
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path("/tmp/icono-geopre-globo.png")
SIZE = 1024
BG = (0xC9, 0x62, 0x3A)        # terracota vivo (fondo)
OCEAN = (0x3B, 0x82, 0xC4)     # azul vivo del oceano
LAND = (0x5F, 0xA8, 0x60)      # verde de los continentes
LAND2 = (0xE8, 0xC8, 0x6A)     # amarillo arena (otro continente)
CREAM = (0xF7, 0xF1, 0xE3)     # casquete polar


def main():
    img = Image.new("RGB", (SIZE, SIZE), BG)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=230, fill=BG)

    # --- Globo (esfera grande, casi todo el marco) ---
    cx, cy, r = 512, 512, 380
    # Capa del globo (para recortar los continentes al circulo).
    layer = Image.new("RGB", (SIZE, SIZE), OCEAN)
    ld = ImageDraw.Draw(layer)
    # Continente grande (izquierda).
    ld.polygon([(250, 380), (330, 320), (420, 350), (450, 430), (400, 520),
                (320, 540), (260, 470)], fill=LAND)
    # Continente mediano (derecha, abajo).
    ld.polygon([(580, 560), (660, 520), (740, 560), (760, 640), (700, 700),
                (620, 680), (580, 620)], fill=LAND)
    # Continente pequeno (derecha, arriba) en arena.
    ld.polygon([(640, 300), (700, 280), (750, 320), (730, 380), (670, 380),
                (640, 340)], fill=LAND2)
    # Isla pequena.
    ld.ellipse([520, 640, 570, 690], fill=LAND)
    # Casquete polar (arriba).
    ld.ellipse([cx - 180, cy - r - 40, cx + 180, cy - r + 130], fill=CREAM)
    # Recortar la capa al circulo del globo.
    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    img.paste(layer, (0, 0), mask)

    img.save(OUT)
    print("icono globo en", OUT)


if __name__ == "__main__":
    main()
