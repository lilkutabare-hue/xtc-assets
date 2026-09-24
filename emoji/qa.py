#!/usr/bin/env python3
"""XTC emoji QA gate: Telegram validator + structural lint + rlottie render checks + contact sheets.

Usage: python3 qa.py <dir_with_tgs> [--sheets OUT_DIR]
Exit code 1 if any file FAILS. Warnings do not fail but must be reviewed.

Install:
  pip install rlottie-python pillow
  SETUPTOOLS_USE_DISTUTILS=stdlib pip install lottie   # plain `pip install lottie` fails on new setuptools
"""
import argparse
import glob
import gzip
import json
import os
import sys

from PIL import Image, ImageChops, ImageFilter
from rlottie_python import LottieAnimation
from lottie.exporters.tgs_validator import TgsValidator, Severity

MARGIN = 8           # px of free canvas around the art on every frame
LOOP_DIFF_MAX = 0.002  # share of canvas pixels that may differ between first and last frame
THIN_WARN = 0.25     # share of art lost after a 28px morphological opening -> too thin for 24px
ONE_D = ("o", "r")   # transform props that rlottie needs as plain scalars when static


def lint(d):
    """Structural rules. Each one was found by rendering real files in rlottie (Telegram's renderer)."""
    errs = []
    if d.get("v") != "5.5.7":
        errs.append("v must be 5.5.7")
    if "meta" in d:
        errs.append("remove meta")
    if d.get("ip") != 0:
        errs.append("ip must be 0")

    def walk(o, path):
        if isinstance(o, dict):
            if o.get("a") == 1 and isinstance(o.get("k"), list):
                ks = o["k"]
                for i, k in enumerate(ks[:-1]):
                    if isinstance(k, dict) and ("i" not in k or "o" not in k) and not k.get("h"):
                        errs.append(f"{path}: keyframe t={k.get('t')} has no i/o easing (rlottie: animated scale -> layer vanishes, rotation/position -> frozen)")
                        break
                last = ks[-1] if ks else {}
                if isinstance(last, dict) and "i" in last:
                    errs.append(f"{path}: last keyframe t={last.get('t')} has 'i' (rlottie breaks the whole property) - give it just t+s")
            for key, v in o.items():
                if key == "x" and isinstance(v, str):
                    errs.append(f"{path}: expression found")
                if key in ("sk", "sa") and isinstance(v, dict) and (v.get("a") == 1 or v.get("k", 0) != 0):
                    errs.append(f"{path}: skew is not supported")
                walk(v, f"{path}.{key}")
            if o.get("ty") in ("fl", "st"):
                c = o.get("c", {})
                if c.get("a") == 1:
                    errs.append(f"{path}: animated color")
                elif [round(x, 4) for x in c.get("k", [0, 0, 0])[:3]] != [0, 0, 0]:
                    errs.append(f"{path}: color is not #000000")
            if o.get("ty") in ("gf", "gs"):
                errs.append(f"{path}: gradient")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")

    for li, layer in enumerate(d.get("layers", [])):
        name = layer.get("nm", f"layer{li}")
        for need in ("ind", "ip", "op", "st", "ks"):
            if need not in layer:
                errs.append(f"{name}: missing {need}")
        if layer.get("ty") not in (3, 4, 0):
            errs.append(f"{name}: layer type {layer.get('ty')} not allowed (only shape/null/precomp)")
        for p in ONE_D:
            prop = layer.get("ks", {}).get(p)
            if prop and prop.get("a") == 0 and isinstance(prop.get("k"), list):
                errs.append(f"{name}: static ks.{p} is an array {prop['k']} - must be a scalar (rlottie renders nothing)")
        walk(layer, name)
    return errs


def colorize(frame, rgb, bg):
    """Simulate Telegram adaptive emoji: only alpha is kept, painted with the text color."""
    a = frame.split()[3]
    solid = Image.new("RGBA", frame.size, rgb + (255,))
    solid.putalpha(a)
    out = Image.new("RGBA", frame.size, bg + (255,))
    out.alpha_composite(solid)
    return out


def check(path):
    fails, warns = [], []
    size = os.path.getsize(path)
    v = TgsValidator(Severity.Note)
    v.check_file(path)
    for e in v.errors:
        (fails if e.severity in (Severity.Error, Severity.Warning) else warns).append(str(e))
    d = json.load(gzip.open(path))
    fails += lint(d)
    if d.get("fr") != 60:
        fails.append(f"fr={d.get('fr')} (brief requires 60)")
    op = d.get("op", 0)
    if not 60 <= op <= 180:
        fails.append(f"op={op} (1.0-3.0 s)")

    anim = LottieAnimation.from_tgs(path)
    n = anim.lottie_animation_get_totalframe()
    frames = [anim.render_pillow_frame(frame_num=i) for i in range(n)]
    empty = [i for i, f in enumerate(frames) if not f.split()[3].point(lambda p: 255 if p > 8 else 0).getbbox()]
    if empty:
        fails.append(f"{len(empty)}/{n} empty frames in rlottie (first: {empty[:5]})")
    box = [512, 512, 0, 0]
    for f in frames:
        bb = f.split()[3].point(lambda p: 255 if p > 8 else 0).getbbox()
        if bb:
            box = [min(box[0], bb[0]), min(box[1], bb[1]), max(box[2], bb[2]), max(box[3], bb[3])]
    if frames and not empty:
        if box[0] < MARGIN or box[1] < MARGIN or box[2] > 512 - MARGIN or box[3] > 512 - MARGIN:
            fails.append(f"art leaves the {MARGIN}px safe margin: bbox {box}")
        span = max(box[2] - box[0], box[3] - box[1]) / 512
        if span < 0.80:
            warns.append(f"art spans only {span:.0%} of canvas (target 88-92%)")
        a0 = frames[0].split()[3]
        # frame op-1 must lead smoothly into frame 0: compare the last frame with frame 0 and frame 1
        last = frames[-1].split()[3]
        diff = sum(ImageChops.difference(a0, last).point(lambda p: 1 if p > 40 else 0).getdata()) / 512 / 512
        step = sum(ImageChops.difference(a0, frames[1].split()[3]).point(lambda p: 1 if p > 40 else 0).getdata()) / 512 / 512 if n > 1 else 0
        if diff > max(LOOP_DIFF_MAX, step * 2.5):
            fails.append(f"loop seam: last->first frame jump {diff:.3%} vs normal step {step:.3%}")
        small = a0.resize((128, 128), Image.LANCZOS).point(lambda p: 255 if p > 128 else 0)
        opened = small.filter(ImageFilter.MinFilter(7)).filter(ImageFilter.MaxFilter(7))
        area = sum(1 for p in small.getdata() if p)
        kept = sum(1 for p in opened.getdata() if p)
        if area and (area - kept) / area > THIN_WARN:
            warns.append(f"{(area - kept) / area:.0%} of the art is thinner than 28px - will blur at 24px")
    if size > 64 * 1024:
        fails.append(f"size {size / 1024:.1f}KB > 64KB")
    # keep only what the sheets need (full-res mid frame + 100px GIF frames): 100+ files x 180 full
    # frames do not fit in RAM. Checks above already ran on every full-res frame.
    keep = {"mid": frames[len(frames) // 3] if frames else None,
            "gif": [f.resize((100, 100), Image.LANCZOS) for f in frames[::2]]}
    return {"file": os.path.basename(path), "kb": round(size / 1024, 1), "frames": n,
            "fails": fails, "warns": warns, "frames_img": keep}


def sheets(results, out):
    os.makedirs(out, exist_ok=True)
    themes = {"light": ((0, 0, 0), (255, 255, 255)), "dark": ((255, 255, 255), (23, 33, 43))}
    cols = 10
    for px in (24, 100):
        for tname, (fg, bg) in themes.items():
            cell = px + 12
            rows = (len(results) + cols - 1) // cols
            sheet = Image.new("RGBA", (cols * cell, rows * cell), bg + (255,))
            for i, r in enumerate(results):
                fr = r["frames_img"]
                if not fr["mid"]:
                    continue
                img = colorize(fr["mid"], fg, bg).resize((px, px), Image.LANCZOS)
                sheet.paste(img, ((i % cols) * cell + 6, (i // cols) * cell + 6))
            sheet.save(os.path.join(out, f"sheet-{px}-{tname}.png"))
    for r in results:
        fr = r["frames_img"]["gif"]
        if not fr:
            continue
        gif = [colorize(f, (0, 0, 0), (255, 255, 255)).convert("RGB") for f in fr]
        gif[0].save(os.path.join(out, r["file"].replace(".tgs", ".gif")), save_all=True,
                    append_images=gif[1:], duration=33, loop=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--sheets")
    a = ap.parse_args()
    results = [check(p) for p in sorted(glob.glob(os.path.join(a.dir, "*.tgs")))]
    bad = 0
    for r in results:
        status = "FAIL" if r["fails"] else ("WARN" if r["warns"] else "OK")
        bad += status == "FAIL"
        print(f"{status:4} {r['file']:32} {r['kb']:5}KB {r['frames']:4}f")
        for m in r["fails"]:
            print("      x", m)
        for m in r["warns"]:
            print("      !", m)
    print(f"\n{len(results) - bad}/{len(results)} pass")
    if a.sheets:
        sheets(results, a.sheets)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
