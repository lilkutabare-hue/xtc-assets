#!/usr/bin/env python3
"""PNG silhouette -> 512 SVG ready for build.py (potrace recipe from the brief).

  python3 trace.py hand-thumbs-up.png src/126-thumbs-up.svg

Input: black shape on white (or on transparency), any size (1024 recommended).
Steps: fit the shape into 512 with the pack's 8px margin + ~90% span, threshold, potrace
(-s -u 1 -t 20 -O 1.0), fix the pt units so lottie/geo.svg read it 1:1 with the PNG.
Then in a spec: g = geo.svg("src/126-thumbs-up.svg") and cut it into parts with shapely.
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageOps

SPAN = 0.9     # art spans 90% of the canvas (brief: 88-92%)


def main(src, dst):
    im = Image.open(src).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    g = ImageOps.grayscale(bg)
    ink = g.point(lambda p: 255 if p < 128 else 0)          # white = ink
    box = ink.getbbox()
    if not box:
        raise SystemExit("no ink found")
    ink = ink.crop(box)
    w, h = ink.size
    k = 512 * SPAN / max(w, h)
    ink = ink.resize((max(1, round(w * k)), max(1, round(h * k))), Image.LANCZOS)
    canvas = Image.new("L", (512, 512), 0)
    canvas.paste(ink, ((512 - ink.width) // 2, (512 - ink.height) // 2))
    big = canvas.resize((1024, 1024), Image.LANCZOS).point(lambda p: 0 if p > 127 else 255)  # potrace: black = ink
    with tempfile.TemporaryDirectory() as d:
        bmp = os.path.join(d, "in.bmp")
        big.convert("1").save(bmp)
        subprocess.run(["potrace", "-s", "-u", "1", "-t", "20", "-O", "1.0", "-W", "512pt", "-H", "512pt", bmp, "-o", dst],
                       check=True)
    s = open(dst).read().replace('width="512.000000pt"', 'width="512"').replace('height="512.000000pt"', 'height="512"')
    s = s.replace('fill="#000000"', 'fill="#000000" fill-rule="evenodd"', 1)
    open(dst, "w").write(s)
    print(dst)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
