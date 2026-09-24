#!/usr/bin/env python3
"""XTC adaptive emoji v2 — build.

  python3 build.py              # build every spec
  python3 build.py 01 hearts    # build specs whose file name contains any of the args
  python3 build.py --view 01    # + review strip into sheets/_view/
  python3 build.py --svg        # + static poster src/NN-name.svg (potrace of the rendered key frame)

Specs live in specs/*.py and register with @emoji(...). Geometry: xtc/geo.py. Keys: xtc/lot.py
(writes the rlottie-safe key format). Motion vocabulary: xtc/motion.py.
"""
import argparse
import importlib
import os
import pkgutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from xtc import lot  # noqa: E402
from xtc.reg import REG  # noqa: E402

import specs  # noqa: E402

for m in pkgutil.iter_modules(specs.__path__):
    try:
        importlib.import_module(f"specs.{m.name}")
    except Exception as e:  # one broken spec module must not stop the others
        print(f"!! specs/{m.name}.py failed to import: {e!r}", file=sys.stderr)


def build(name):
    e = REG[name]
    c = lot.Comp(name, op=e["op"])
    e["fn"](c)
    out = os.path.join(HERE, "tgs", name + ".tgs")
    c.save(out)
    return out


def poster_svg(tgs, name, frame=None):
    from rlottie_python import LottieAnimation
    a = LottieAnimation.from_tgs(tgs)
    n = a.lottie_animation_get_totalframe()
    fr = a.render_pillow_frame(frame_num=frame if frame is not None else 0, width=1024, height=1024)
    alpha = fr.split()[3].point(lambda p: 0 if p > 127 else 255)
    with tempfile.TemporaryDirectory() as d:
        bmp = os.path.join(d, "f.bmp")
        alpha.convert("1").save(bmp)
        svg = os.path.join(HERE, "src", name + ".svg")
        subprocess.run(["potrace", "-s", "-u", "1", "-t", "10", "-O", "0.5", "-W", "512pt", "-H", "512pt", bmp, "-o", svg], check=True)
        s = open(svg).read().replace('width="512.000000pt"', 'width="512"').replace('height="512.000000pt"', 'height="512"')
        s = s.replace('fill="#000000"', 'fill="#000000" fill-rule="evenodd"', 1)
        open(svg, "w").write(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--view", action="store_true")
    ap.add_argument("--svg", action="store_true")
    ap.add_argument("--multi", action="store_true", help="one combined review image for all built")
    a = ap.parse_args()
    names = sorted(n for n in REG if not a.names or any(x in n for x in a.names))
    for n in names:
        out = build(n)
        print(f"{n:34} {os.path.getsize(out) / 1024:5.1f}KB")
        if a.view:
            from xtc import view
            os.makedirs(os.path.join(HERE, "sheets", "_view"), exist_ok=True)
            view.strip(out, os.path.join(HERE, "sheets", "_view", n + ".png"))
            view.grid(out, os.path.join(HERE, "sheets", "_view", n + "-grid.png"))
        if a.svg:
            poster_svg(out, n, REG[n].get("poster"))
    if a.multi:
        from xtc import view
        os.makedirs(os.path.join(HERE, "sheets", "_view"), exist_ok=True)
        print(view.multi([os.path.join(HERE, "tgs", n + ".tgs") for n in names],
                         os.path.join(HERE, "sheets", "_view", "_multi.png")))


if __name__ == "__main__":
    main()
