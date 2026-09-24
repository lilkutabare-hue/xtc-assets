"""Review strip for one or many .tgs: frames at 128px (adaptive-colourised), 24px light/dark, onion skin."""
import sys

from PIL import Image, ImageChops, ImageDraw
from rlottie_python import LottieAnimation


def frames_of(path):
    a = LottieAnimation.from_tgs(path)
    n = a.lottie_animation_get_totalframe()
    return [a.render_pillow_frame(frame_num=i) for i in range(n)]


def colorize(fr, fg, bg):
    a = fr.split()[3]
    solid = Image.new("RGBA", fr.size, fg + (255,))
    solid.putalpha(a)
    out = Image.new("RGBA", fr.size, bg + (255,))
    out.alpha_composite(solid)
    return out


def strip(path, out, picks=None, cell=128):
    fr = frames_of(path)
    n = len(fr)
    picks = picks or [round(i * (n - 1) / 11) for i in range(12)]
    cols = len(picks) + 2
    W = cell * cols
    img = Image.new("RGB", (W, cell + 40 + 18), (235, 235, 235))
    d = ImageDraw.Draw(img)
    for j, i in enumerate(picks):
        c = colorize(fr[i], (0, 0, 0), (255, 255, 255)).resize((cell - 4, cell - 4), Image.LANCZOS)
        img.paste(c.convert("RGB"), (j * cell + 2, 2))
        d.text((j * cell + 4, cell - 12), str(i), fill=(200, 0, 0))
    # onion skin (union of alpha over all frames) + 8px margin box
    on = Image.new("L", (512, 512), 0)
    for f in fr:
        on = ImageChops.lighter(on, f.split()[3])
    c = Image.new("RGB", (512, 512), (255, 255, 255))
    c.paste((120, 120, 255), (0, 0), on)
    dd = ImageDraw.Draw(c)
    dd.rectangle((8, 8, 503, 503), outline=(255, 0, 0), width=3)
    img.paste(c.resize((cell - 4, cell - 4)), (len(picks) * cell + 2, 2))
    # 24px samples of 4 frames, light + dark, upscaled x2 nearest for inspection
    x = 2
    for i in picks[::3]:
        for fg, bg in (((0, 0, 0), (255, 255, 255)), ((255, 255, 255), (23, 33, 43))):
            s = colorize(fr[i], fg, bg).resize((24, 24), Image.LANCZOS).convert("RGB")
            img.paste(s, (x, cell + 6))
            x += 28
    # 24px frame at native size, plus 100px picker size of mid frame
    p100 = colorize(fr[n // 3], (255, 255, 255), (23, 33, 43)).resize((100, 100), Image.LANCZOS).convert("RGB")
    img.paste(p100.resize((cell - 4, cell - 4)), ((len(picks) + 1) * cell + 2, 2))
    d.text((x + 10, cell + 12), path.split("/")[-1], fill=(0, 0, 0))
    img.save(out)
    return out


if __name__ == "__main__":
    strip(sys.argv[1], sys.argv[2])


def grid(path, out, step=3, cell=96, cols=15):
    """every `step`-th frame in a grid: the closest thing to watching the GIF frame by frame."""
    fr = frames_of(path)
    idx = list(range(0, len(fr), step))
    rows = (len(idx) + cols - 1) // cols
    img = Image.new("RGB", (cols * cell, rows * cell), (235, 235, 235))
    d = ImageDraw.Draw(img)
    for j, i in enumerate(idx):
        c = colorize(fr[i], (0, 0, 0), (255, 255, 255)).resize((cell - 2, cell - 2), Image.LANCZOS)
        x, y = (j % cols) * cell, (j // cols) * cell
        img.paste(c.convert("RGB"), (x + 1, y + 1))
        d.text((x + 3, y + cell - 12), str(i), fill=(200, 0, 0))
    img.save(out)
    return out


def multi(paths, out, step=6, cell=72, cols=None):
    """several emoji, one row each (every `step` frames) — batch review."""
    rows = []
    for p in paths:
        fr = frames_of(p)
        idx = list(range(0, len(fr), step))
        row = Image.new("RGB", (cell * (len(idx) + 2), cell), (235, 235, 235))
        d = ImageDraw.Draw(row)
        for j, i in enumerate(idx):
            c = colorize(fr[i], (0, 0, 0), (255, 255, 255)).resize((cell - 2, cell - 2), Image.LANCZOS)
            row.paste(c.convert("RGB"), (j * cell + 1, 1))
            d.text((j * cell + 2, cell - 11), str(i), fill=(200, 0, 0))
        x = len(idx) * cell + 4
        for fg, bg in (((0, 0, 0), (255, 255, 255)), ((255, 255, 255), (23, 33, 43))):
            s = colorize(fr[len(fr) // 3], fg, bg).resize((24, 24), Image.LANCZOS).convert("RGB")
            row.paste(s, (x, 4))
            x += 28
        d.text((len(idx) * cell + 4, 34), p.split("/")[-1][:14], fill=(0, 0, 0))
        rows.append(row)
    W = max(r.width for r in rows)
    img = Image.new("RGB", (W, cell * len(rows)), (200, 200, 200))
    for i, r in enumerate(rows):
        img.paste(r, (0, i * cell))
    img.save(out)
    return out
