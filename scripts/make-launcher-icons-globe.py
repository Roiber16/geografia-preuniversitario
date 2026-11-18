#!/usr/bin/env python3
"""Genera los iconos legacy de la APK desde el globo v3.

El globo (1024x1024, fondo terracota a sangre) ya es a sangre completa,
asi que solo se escala a cada densidad. Se reemplazan los tres PNG de
cada densidad (ic_launcher, ic_launcher_foreground e ic_launcher_round)
para que no quede ningun icono viejo (Atlas ni Capacitor) en la APK.
El round lleva mascara circular.
"""
from pathlib import Path
from PIL import Image, ImageDraw

SRC = Path("/tmp/icono-geopre-globo.png")
RES = Path("/home/hatch/workspace/geografia-apk/android/app/src/main/res")
SIZES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}


def main():
    src = Image.open(SRC).convert("RGB")
    for density, size in SIZES.items():
        d = RES / f"mipmap-{density}"
        d.mkdir(parents=True, exist_ok=True)
        icon = src.resize((size, size), Image.LANCZOS)
        for name in ("ic_launcher.png", "ic_launcher_foreground.png"):
            icon.save(d / name)
        # Round: mascara circular sobre el mismo globo.
        m = Image.new("L", (size, size), 0)
        ImageDraw.Draw(m).ellipse([0, 0, size - 1, size - 1], fill=255)
        rnd = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        rnd.paste(icon.convert("RGBA"), (0, 0), m)
        rnd.save(d / "ic_launcher_round.png")
        print(density, size, "ok")
    print("iconos globo listos")


if __name__ == "__main__":
    main()
