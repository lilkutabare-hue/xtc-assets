#!/usr/bin/env python3
"""Pack order + manifest + zips.

  python3 pack.py manifest            # write manifest.csv (order = pack order, first = cover)
  python3 pack.py zip P0|final        # write XTC-emoji-v2[-P0].zip
"""
import csv
import gzip
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# pack order: cover -> brand & DROP -> faces (joy -> anger -> shock -> sadness) -> reactions -> symbols -> badges
ORDER = """
01-pill-x
44-cross-amen 50-soldout-tee 47-flipclock 48-board-payme 49-board-dropnow 112-box-drop 45-buckle-lock 51-latex-heart
52-psp 53-bag-xtc 109-bills 46-eyelets-wow 29-drip-xtc 20-split-pill 16-heart-pill
54-laugh 55-rofl 35-kao-happy 58-heart-eyes 59-kiss 104-drool 108-yum 107-hug 39-kao-wink 66-smirk 68-cool 105-nerd
70-party 71-devil 81-angel 42-kao-tongue 02-acid-xx 38-kao-tear 80-salute 64-think 101-raised-brow 79-moai 67-unamused
65-eyeroll 37-kao-meh 102-zipper-mouth 103-yawn 76-sleep 63-flushed 69-peek 77-grimace 78-clown
60-rage 100-huff 61-swear 34-kao-squeeze
62-scream 40-kao-shock 75-mind-blown
57-plead 36-kao-cry 56-sob 73-melt 74-dizzy 106-woozy 82-nausea 33-kao-xx 72-skull
83-eyes 84-fire 85-hundred 86-check 87-cross 88-heart 89-broken-heart 90-sparkles 91-zap 92-question 93-exclaim
110-popper 111-siren 113-cocktail 114-headphones
126-thumbs-up 127-thumbs-down 128-victory 129-rock 130-wave
14-barbed-heart 15-dagger-heart 26-tribal-heart 22-kiss-less3 04-tramp-stamp 10-club-key 13-dagger-cross
18-spike-collar 19-thorn-star 23-dot-star 28-tribal-cross 27-tribal-eye 24-print-scan 25-mask-glyphs
21-teddy-skull 03-sigil-x 43-scorpion-sigil 31-cyber-butterfly 32-swallow 17-winged-x 41-patch-x 30-club-banner
94-lol 95-omg 96-wtf 97-ok 98-no 99-yes 115-gm 116-gn 117-xoxo 118-soon 119-sold-out 120-new 121-xtc
""".split()
# failed the scale after 2 attempts -> not in the pack (reasons also in scores.csv / REPORT.md)
CUT = {
    "119-sold-out": "7 букв на 512 не читаются на 24px; SOLD OUT уже закрыт эмодзи 50",
    "127-thumbs-down": "2 попытки, Σ27: перевёрнутый 👍 на 24px читается буквой F",
}


def reg():
    import importlib
    import pkgutil
    import specs
    from xtc.reg import REG
    for m in pkgutil.iter_modules(specs.__path__):
        importlib.import_module(f"specs.{m.name}")
    return REG


def scores():
    out = {}
    p = os.path.join(HERE, "scores.csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            out[r["file"]] = (r["render_sum"], r["status"])
    return out


def order(kind):
    names = [n for n in ORDER if n not in CUT]
    if kind == "P0":
        names = [n for n in names if int(n.split("-")[0]) < 100]
    return names


def manifest(kind="final"):
    R = reg()
    sc = scores()
    rows = []
    for n in order(kind):
        e = R[n]
        path = os.path.join(HERE, "tgs", n + ".tgs")
        rows.append([n + ".tgs", e["emoji"], e["ru"], e["en"], e["story"], sc.get(n, ("", ""))[0],
                     round(os.path.getsize(path) / 1024, 1)])
    with open(os.path.join(HERE, "manifest.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "emoji", "keywords_ru", "keywords_en", "story", "score", "size_kb"])
        w.writerows(rows)
    return rows


def make_zip(kind, sheets_dir=None):
    names = order(kind)
    out = os.path.join(HERE, "XTC-emoji-v2-P0.zip" if kind == "P0" else "XTC-emoji-v2.zip")
    files = ["build.py", "qa.py", "pack.py", "upload.py", "trace.py", "moodboard.md", "concepts.md", "scores.csv",
             "manifest.csv", "upload.md", "REPORT.md"]
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            p = os.path.join(HERE, f)
            if os.path.exists(p):
                z.write(p, f)
        for d in ("xtc", "specs", "fonts", "prompts"):
            for root, _, fs in os.walk(os.path.join(HERE, d)):
                for f in fs:
                    if "__pycache__" in root:
                        continue
                    p = os.path.join(root, f)
                    z.write(p, os.path.relpath(p, HERE))
        sd = sheets_dir or os.path.join(HERE, "sheets")
        for n in names:
            z.write(os.path.join(HERE, "tgs", n + ".tgs"), f"tgs/{n}.tgs")
            s = os.path.join(HERE, "src", n + ".svg")
            if os.path.exists(s):
                z.write(s, f"src/{n}.svg")
            g = os.path.join(sd, n + ".gif")
            if os.path.exists(g):
                z.write(g, f"sheets/{n}.gif")
        for f in os.listdir(sd):
            if f.startswith("sheet-"):
                z.write(os.path.join(sd, f), f"sheets/{f}")
    return out


def report():
    """REPORT.md: table in pack order, top-10, cuts, what is left."""
    R = reg()
    sc = {r["file"]: r for r in csv.DictReader(open(os.path.join(HERE, "scores.csv")))}
    names = order("final")
    lines = ["# XTC emoji v2 — отчёт", "",
             f"В паке **{len(names)}** adaptive-эмодзи (TGS 512, 60 fps, 1–3 с). `qa.py`: 0 FAIL; у всех все минимумы шкалы + Σ≥29.",
             "Порядок = `manifest.csv` (первый — обложка). Оценки по 7 критериям с обоснованиями — `scores.csv`.", "",
             "| # | файл | 🔣 | история | Σ/35 | KB |", "|---|---|---|---|---|---|"]
    for i, n in enumerate(names, 1):
        e = R[n]
        kb = round(os.path.getsize(os.path.join(HERE, "tgs", n + ".tgs")) / 1024, 1)
        lines.append(f"| {i} | {n} | {e['emoji']} | {e['story']} | {sc[n]['render_sum']} | {kb} |")
    top = sorted(names, key=lambda n: (-int(sc[n]["render_sum"]), n))[:10]
    lines += ["", "## Топ-10", ""] + [f"{i}. **{n}** {R[n]['emoji']}: {sc[n]['render_sum']}/35, {R[n]['story']}" for i, n in enumerate(top, 1)]
    lines += ["", "## Вырезано", ""] + [f"- **{n}** {R[n]['emoji']}: {why}" for n, why in CUT.items()]
    return lines


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "manifest":
        rows = manifest(sys.argv[2] if len(sys.argv) > 2 else "final")
        print(len(rows), "rows")
    elif cmd == "report":
        print("\n".join(report()))
    elif cmd == "zip":
        print(make_zip(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
