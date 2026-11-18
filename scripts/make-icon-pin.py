#!/usr/bin/env python3
"""Icono plano de GeoPre v2: pin de mapa con un globo dentro.

El globo con meridianos parecia un atomo. Este es un pin de mapa
(lagrimas terracota) con un globo pequeno dentro, sin meridianos y con
una sola mancha de tierra. Todo plano, dibujado por codigo, sin IA.
"""
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path("/tmp/icono-geopre-pin.png")
SIZE = 1024
BG = (0x56, 0x76, 0x92)        # azul pizarra de la marca
TERRA = (0xC9, 0x62, 0x3A)     # terracota del pin
CREAM = (0xF7, 0xF1, 0xE3)     # circulo interior
GLOBE = (0xA8, 0xC8, 0xE0)     # azul claro del globo


def main():
    img = Image.new("RGB", (SIZE, SIZE), BG)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=230, fill=BG)

    # --- Pin de mapa (silueta: circulo + triangulo, una sola pieza) ---
    mask = Image.new("L", (SIZE, SIZE), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([512 - 290, 430 - 290, 512 + 290, 430 + 290], fill=255)
    md.polygon([(512 - 250, 600), (512 + 250, 600), (512, 925)], fill=255)
    pin = Image.new("RGB", (SIZE, SIZE), TERRA)
    img.paste(pin, (0, 0), mask)
    d = ImageDraw.Draw(img)

    # --- Globo dentro del pin ---
    gx, gy, gr = 512, 430, 145
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=GLOBE)
    # Una sola mancha de tierra (forma irregular, no un circulo).
    land = [(470, 340), (520, 325), (560, 350), (575, 395), (545, 430),
            (560, 470), (520, 500), (475, 480), (450, 430), (455, 380)]
    d.polygon(land, fill=TERRA)
    # Punto pequeno (una isla).
    d.ellipse([gx + 55, gy + 55, gx + 95, gy + 95], fill=TERRA)

    img.save(OUT)
    print("icono pin en", OUT)


if __name__ == "__main__":
    main()
