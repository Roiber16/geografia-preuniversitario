#!/usr/bin/env python3
"""Genera los iconos legacy de la APK desde el globo en blanco y negro
elegido por Roi (1000373519_2_c97x.jpg).

La foto es 720x557 (apaisada): se recorta centrada a cuadrado para no
deformar el globo y se escala a cada densidad. Se reemplazan los tres
PNG de cada densidad para que no quede ningun icono viejo.
"""
from pathlib import Path
from PIL import Image, ImageDraw

SRC = Path("/home/hatch/workspace/user/files/1000373519_2_c97x.jpg")
RES = Path("/home/hatch/workspace/geografia-apk/android/app/src/main/res")
SIZES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}


def main():
    src = Image.open(SRC).convert("RGB")
    w, h = src.size
    s = min(w, h)
    sq = src.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
    for density, size in SIZES.items():
        d = RES / f"mipmap-{density}"
        d.mkdir(parents=True, exist_ok=True)
        icon = sq.resize((size, size), Image.LANCZOS)
        for name in ("ic_launcher.png", "ic_launcher_foreground.png"):
            icon.save(d / name)
        m = Image.new("L", (size, size), 0)
        ImageDraw.Draw(m).ellipse([0, 0, size - 1, size - 1], fill=255)
        rnd = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        rnd.paste(icon.convert("RGBA"), (0, 0), m)
        rnd.save(d / "ic_launcher_round.png")
        print(density, size, "ok")
    print("iconos blanco y negro listos")


if __name__ == "__main__":
    main()
