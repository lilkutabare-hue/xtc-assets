"""PSP promo, Obsidian look: keyframes for Kling 3.0 (start/end frames).

    python3 promo/psp/build.py [plate.png]

Input plate: front render of the XTC console on transparent background
(default app/psp/plate.webp). Needs numpy + pillow. Writes 1080x1920 PNGs
into promo/psp/obsidian/.
"""
import sys, os
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'promo/psp/obsidian')
PLATE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'app/psp/plate.webp')
# plate geometry, px in the plate: body box (without shoulder bumpers), screen, wordmark area
BODY = (129, 130, 2270, 1027)
SCREEN = (573, 160, 1826, 880)
WORDMARK = (950, 905, 1352, 962)

W, H = 1080, 1920
PINK = np.array([255, 79, 163], np.float32)
rng = np.random.default_rng(11)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
os.makedirs(OUT, exist_ok=True)


def plates():
    q = np.asarray(Image.open(PLATE).convert('RGBA')).astype(np.float32)
    ph, pw = q.shape[:2]
    rgb, a = q[..., :3], q[..., 3]
    L = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    py, px = np.mgrid[0:ph, 0:pw]
    X0, Y0, X1, Y1 = SCREEN
    m = Image.new('L', (pw * 4, ph * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle((X0 * 4, Y0 * 4, X1 * 4 + 3, Y1 * 4 + 3), radius=56, fill=255)
    M = np.asarray(m.resize((pw, ph), Image.LANCZOS)).astype(np.float32)[..., None] / 255
    # clean glossy-black screen: soft top-left sheen, no baked reflection streak
    u, v = (px - X0) / (X1 - X0), (py - Y0) / (Y1 - Y0)
    sheen = np.clip(1 - np.sqrt((u * 0.9) ** 2 + (v * 1.6) ** 2), 0, 1) ** 2.2 * 26
    scr = np.stack([7 + sheen, 7 + sheen, 9 + sheen * 1.05], -1)
    pink = Image.fromarray(np.clip(np.dstack([rgb * (1 - M) + scr * M, a]), 0, 255).astype(np.uint8), 'RGBA')
    # obsidian cast of the same body: black lacquer, highlights kept, no wordmark
    s = np.clip((L - 115) / 115, 0, 1) ** 2
    spec = np.clip((L - 214) / 22, 0, 1) ** 2
    ob = np.stack([5 + 30 * s + 190 * spec, 5 + 30 * s + 190 * spec, 7 + 33 * s + 196 * spec], -1)
    ob[a < 250] = (np.stack([L, L, L * 1.03], -1) * 0.33)[a < 250]
    wx0, wy0, wx1, wy1 = WORDMARK
    txt = (L > 228) & (py >= wy0) & (py <= wy1) & (px >= wx0) & (px <= wx1)
    t2 = np.asarray(Image.fromarray((txt * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))) > 0
    for x in range(wx0, wx1 + 1):
        col = np.where(t2[:, x])[0]
        if len(col):
            y0, y1 = col.min() - 2, col.max() + 2
            top, bot = ob[y0, x].copy(), ob[y1, x].copy()
            t = ((np.arange(y0, y1 + 1) - y0) / max(1, y1 - y0))[:, None]
            ob[y0:y1 + 1, x] = top * (1 - t) + bot * t
    obsidian = Image.fromarray(np.clip(np.dstack([ob * (1 - M) + scr * M, a]), 0, 255).astype(np.uint8), 'RGBA')
    return pink, obsidian


def backdrop():
    bg = np.zeros((H, W, 3), np.float32) + [4, 4, 5]
    d = np.sqrt(((xx - 540) / 640) ** 2 + ((yy - 900) / 620) ** 2)
    bg += np.clip(1 - d, 0, 1)[..., None] ** 1.8 * [22, 21, 26]      # charcoal glow so black reads on black
    d = np.sqrt(((xx - 540) / 560) ** 2 + ((yy - 1300) / 70) ** 2)
    bg += np.clip(1 - d, 0, 1)[..., None] ** 1.5 * [16, 16, 19]      # light pool on the floor
    return bg


def add(dst, rgba, x, y):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); lay.paste(rgba, (x, y))
    l = np.asarray(lay).astype(np.float32); al = l[..., 3:] / 255
    return dst * (1 - al) + l[..., :3] * al


def light(dst, rgb, alpha):
    return dst + rgb * alpha[..., None]


def blurred_alpha(rgba, x, y, r):
    A = Image.new('L', (W, H), 0); A.paste(rgba.getchannel('A'), (x, y))
    return np.asarray(A.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255


def save(img, name, grain=2.6):
    v = np.clip(1 - 0.55 * (((xx - 540) / 760) ** 2 + ((yy - 900) / 1250) ** 2), 0.35, 1)[..., None]
    img = img * v + rng.normal(0, grain, (H, W, 1))
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(os.path.join(OUT, name))


PW = 940  # console width in frame, bumpers included


def place(bg, plate, cy=1000, glow=0.0, screen_img=None):
    s = PW / (BODY[2] - BODY[0])
    p = plate.resize((round(plate.size[0] * s), round(plate.size[1] * s)), Image.LANCZOS)
    bx = round(540 - (BODY[0] + BODY[2]) / 2 * s); by = round(cy - (BODY[1] + BODY[3]) / 2 * s)
    X0, Y0, X1, Y1 = SCREEN
    sr = (bx + round(X0 * s), by + round(Y0 * s), bx + round(X1 * s), by + round(Y1 * s))
    if screen_img is not None:
        p = p.copy(); p.alpha_composite(screen_img.convert('RGBA').resize((sr[2] - sr[0], sr[3] - sr[1]), Image.LANCZOS), (round(X0 * s), round(Y0 * s)))
    bottom = by + round(BODY[3] * s); floor = bottom + 70          # levitates 70 px above the floor
    img = bg.copy()
    d = np.sqrt(((xx - 540) / 430) ** 2 + ((yy - floor) / 22) ** 2)
    img *= 1 - 0.55 * np.clip(1 - d, 0, 1)[..., None] ** 1.2
    refl = p.transpose(Image.FLIP_TOP_BOTTOM).filter(ImageFilter.GaussianBlur(2.2))
    ra = np.asarray(refl).astype(np.float32); hh = ra.shape[0]
    ra[..., 3] *= (np.clip(1 - np.arange(hh) / (hh * 0.62), 0, 1) ** 1.6 * 0.30)[:, None]
    img = add(img, Image.fromarray(ra.astype(np.uint8), 'RGBA'), bx, floor + (floor - bottom) - (p.size[1] - round(BODY[3] * s)))
    if glow > 0:
        img = light(img, PINK, blurred_alpha(p, bx, by, 60) * glow * 0.55)
        d = np.sqrt(((xx - 540) / 520) ** 2 + ((yy - floor - 40) / 60) ** 2)
        img = light(img, PINK, np.clip(1 - d, 0, 1) ** 1.4 * glow * 0.35)
    return add(img, p, bx, by), sr


def lit_screen(sr):
    w, h = sr[2] - sr[0], sr[3] - sr[1]
    u = np.linspace(-1, 1, w)[None, :]; v = np.linspace(0, 1, h)[:, None]
    g = (np.clip(1 - np.sqrt((u * 0.85) ** 2 + ((v - 0.15) * 1.3) ** 2), 0, 1) ** 1.3)[..., None]
    arr = np.zeros((h, w, 4), np.float32)
    arr[..., :3] = PINK * (0.62 + 0.38 * g) * (1 - g ** 2) + np.array([255, 236, 246], np.float32) * g ** 2
    arr[..., 3] = 255
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')


def beam(img, sr):
    cx, top = (sr[0] + sr[2]) / 2, sr[1]
    t = np.clip((top - yy) / top, 0, 1)
    half = (sr[2] - sr[0]) * 0.42 * (1 + 0.35 * t)
    above = yy < top
    img = light(img, PINK, np.clip(1 - np.abs(xx - cx) / half, 0, 1) ** 1.6 * (1 - t) ** 0.9 * above * 0.55)
    core = np.clip(1 - np.abs(xx - cx) / (half * 0.25), 0, 1) ** 2 * (1 - t) ** 1.3 * above
    return light(img, np.array([255, 210, 235], np.float32), core * 0.35)


def loot_item(img, path, width, cy, deg):
    im = Image.open(path).convert('RGBA'); im = im.crop(im.getchannel('A').getbbox())
    k = width / im.size[0]; im = im.resize((round(im.size[0] * k), round(im.size[1] * k)), Image.LANCZOS)
    pad = max(im.size) // 3
    c = Image.new('RGBA', (im.size[0] + 2 * pad, im.size[1] + 2 * pad), (0, 0, 0, 0)); c.paste(im, (pad, pad))
    c = c.rotate(deg, resample=Image.BICUBIC)
    x0, y0 = 540 - c.size[0] // 2, cy - c.size[1] // 2
    img = light(img, PINK, blurred_alpha(c, x0, y0, 18) * 0.42)                  # pink back light
    ca = np.asarray(c).astype(np.float32); hh = ca.shape[0]
    ramp = (np.clip((np.arange(hh) / hh - 0.55) / 0.45, 0, 1) * 0.18)[:, None, None]
    ca[..., :3] = ca[..., :3] * (1 - ramp) + PINK * ramp                            # bounce from the beam
    return add(img, Image.fromarray(np.clip(ca, 0, 255).astype(np.uint8), 'RGBA'), x0, y0)


def macro(plate, name, x0):
    bg = np.zeros((H, W, 3), np.float32) + [4, 4, 5]
    d = np.sqrt(((xx - 540) / 700) ** 2 + ((yy - 960) / 700) ** 2)
    bg += np.clip(1 - d, 0, 1)[..., None] ** 1.8 * [24, 18, 24]
    crop = plate.crop((x0, 0, x0 + W, plate.size[1]))
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); lay.paste(crop, (0, (H - crop.size[1]) // 2))
    l = np.asarray(lay).astype(np.float32); al = l[..., 3:] / 255
    fall = np.clip(1.05 - 0.55 * ((yy - 380) / 1160), 0.35, 1.05)[..., None]     # key light from the top
    save(bg * (1 - al) + l[..., :3] * fall * al, name, grain=2.4)


if __name__ == '__main__':
    pink, obsidian = plates()
    bg = backdrop()
    img, sr = place(bg, obsidian); save(img, 'F1-obsidian-psp.png')
    img, sr = place(bg, pink, glow=0.6); save(img, 'F3-pink-xtc.png')
    for name, path, width, cy, deg in (
        ('L1-longsleeve.png', 'products/night-longsleeve/01.webp', 560, 400, -4),
        ('L2-latex-pants.png', 'products/latex-pants/black-front.webp', 400, 390, 5),
        ('L3-belt.png', 'products/belt/rolled-pink.webp', 560, 440, -8),
        ('L4-bag.png', 'promo/psp/src/bag-xtc-dark-front.png', 450, 410, 6),
    ):
        img, _ = place(bg, pink, glow=0.9, screen_img=lit_screen(sr))
        save(loot_item(beam(img, sr), os.path.join(ROOT, path), width, cy, deg), name)
    fb = Image.open(os.path.join(ROOT, 'drop/loop.gif')); fb.seek(0); fb = fb.convert('RGBA')
    img, _ = place(bg, pink, glow=0.6, screen_img=fb.crop(fb.getbbox())); save(img, 'F5-cta-flipboard.png')
    macro(pink, 'M1-macro-buttons.png', 1320)
    macro(pink, 'M2-macro-dpad.png', 0)
    print('screen rect in frame (x0 y0 x1 y1):', *sr)
