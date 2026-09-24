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
148-broken-heart 44-cross-amen 146-cross-xtc 144-cross-pendant 145-iron-cross 28-tribal-cross 138-seal 136-flash 50-soldout-tee 134-louverse-tank 47-flipclock 49-board-dropnow
131-tile-x 132-tile-t 133-tile-c 121-xtc 112-box-drop 109-bills 52-psp 53-bag-xtc 29-drip-xtc 51-latex-heart 20-split-pill 16-heart-pill
33-kao-xx 56-sob
87-cross 90-sparkles 84-fire 111-siren
10-club-key 21-teddy-skull 26-tribal-heart 04-tramp-stamp 22-kiss-less3
03-sigil-x 43-scorpion-sigil 27-tribal-eye 17-winged-x 18-spike-collar 19-thorn-star 41-patch-x 147-raven 25-mask-glyphs
""".split()
# not in v3 (reasons: REVIEW-v3.md)
CUT_V2 = {
    "119-sold-out": "7 букв на 512 не читаются на 24px; SOLD OUT уже закрыт эмодзи 50",
    "127-thumbs-down": "2 попытки, Σ27: перевёрнутый 👍 на 24px читается буквой F",
}
CUT_V3 = """
46-eyelets-wow 55-rofl 62-scream 63-flushed 64-think 65-eyeroll 66-smirk 67-unamused 69-peek 70-party 71-devil
74-dizzy 76-sleep 77-grimace 78-clown 79-moai 80-salute 81-angel 82-nausea 100-huff 101-raised-brow 103-yawn
104-drool 105-nerd 106-woozy 107-hug 108-yum 34-kao-squeeze 35-kao-happy 36-kao-cry 37-kao-meh
38-kao-tear 39-kao-wink 40-kao-shock 42-kao-tongue
02-acid-xx 139-xx 140-laugh 141-cry 142-cool 143-melt 114-headphones 14-barbed-heart 15-dagger-heart 13-dagger-cross 32-swallow
54-laugh 57-plead 58-heart-eyes 59-kiss 60-rage 61-swear 68-cool 72-skull 73-melt 75-mind-blown 83-eyes 102-zipper-mouth
91-zap 92-question 93-exclaim 110-popper 126-thumbs-up 128-victory 129-rock 130-wave
85-hundred 86-check 88-heart 89-broken-heart 113-cocktail
23-dot-star 24-print-scan 30-club-banner 31-cyber-butterfly
45-buckle-lock 135-latexx-pants 137-tee-daynight 48-board-payme
94-lol 95-omg 96-wtf 97-ok 98-no 99-yes 115-gm 116-gn 117-xoxo 118-soon 120-new
""".split()
CUT = dict(CUT_V2)
CUT.update({n: "см. REVIEW-v3.md" for n in CUT_V3})


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
    out = os.path.join(HERE, "XTC-emoji-v3-P0.zip" if kind == "P0" else "XTC-emoji-v3.zip")
    files = ["build.py", "qa.py", "pack.py", "upload.py", "trace.py", "moodboard.md", "concepts.md", "scores.csv",
             "manifest.csv", "upload.md", "REPORT.md", "STYLE.md", "REVIEW-v3.md"]
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


V3_MD = """## Было → стало (v2 → v3.3)

**Претензии клиента к v2:** много рожиц («0_0»), нет единого свэга, кринж, нужно «экспенсив» и инновационно.
**Правки после v3.0:** только наши знаки (логотип 1:1), лица не kaomoji, ремни/штаны/чужие тексты убрать, тату-капсулу и мишку вернуть, рожиц гораздо меньше, X_X.

| | v2 | v3.1 |
|---|---|---|
| эмодзи в паке | 117 | 45 |
| лиц | 55 (kaomoji) | 2 (X_X логотипными X, T_T) |
| из них «0_0» | 9 | 0 |
| логотип | шрифт Michroma «под лого», пропорции разные в каждом месте | трассировка брендового файла 1:1 (`fonts/xtc-logo.svg`, `xtc/logo.py`); одна пропорция 2.2:1 (как принт лонгслива) и одна жирность во всех 25 местах |
| тексты на табло | LOL/OMG/WTF/OK/NO/YES/GM/GN/XOXO/SOON/NEW/PAY ME | только X·T·C (плитки-пазл, 121) и DROP NOW |
| порог шкалы | Σ≥29, брендовость ≥3 | каждый критерий ≥4, плавность/луп = 5, Σ≥31, свэг-тест STYLE.md |
| средняя Σ | 30.6 | 31.8 |

**Состав v3.3:** 24 бренд-предмета (+ кресты: логотип-крест в плашке, готическая подвеска, железный крест; разбитое сердце с лого) (таблетка, крест, печать, вспышка, лонгслив SOLD OUT, louverse tank, таймер, DROP NOW, плитки X·T·C, XTC-плитки, коробка, купюры, PSP, сумка, XTC-подтёки, латекс-сердце, таблетка-магнит, сердце-таблетка) · 2 лица (X_X, T_T) · 4 реакции с логотипом (X-штамп, хром-X, X-пламя, мигалка-X) · 15 тату v1 (ключ, мишка с костями, трайбл-сердца, сигилы, звезда, пластырь, ворон, маска).

**Новые вау (v3.0 + v3.1):**

| файл | приём |
|---|---|
| 131/132/133 tile-x/t/c | пазл: три плитки закрепа с одним op=150 и флапами на к.40/76; подряд в тексте = табло `X T C`. Риск: Telegram не гарантирует синхронный старт лупов трёх эмодзи в одной строке; при одновременном появлении в одном сообщении они идут синхронно |
| 134 louverse-tank | XTC выложено люверсами на майке; люверсы моргают волной (кольцо → щель), ткань дышит, блик по ткани |
| 136 flash | негатив на 3 кадра: карточка с крест-лого инвертируется (чёрное ↔ дырка), «проявляется» с пережогом 106% |
| 138 seal | клише давит сургуч (slam 112/86), поднимается — оттиск X·XTC·C дыркой, к концу лупа заплывает |
| 52 psp | понг внутри экрана-дырки: чёрные ракетки и шарик на цвете фона, кнопки жмутся в такт, game over = XTC |
| 87 / 90 | логотипный X как штамп с бликом и как хромовая вещь с ✦-вырезами |
| 144 / 145 / 146 | кресты: подвеска-маятник с разворотом, железный штамп с переворотом (X на обороте), плашка с логотипом-крестом насквозь |
| 148 | разбитое сердце: логотип-X рвётся по трещине, латекс капает из разлома |
| 147 | ворон: тяжёлые взмахи (slam вниз / decel вверх), дальнее крыло с лагом |

**Вырезано 71 из 117 v2 + 9 своих (v3.0/v3.1):** 53 лица (kaomoji и семейство кислотного смайла — клиент: «очень плохие»), 4 руки, 12 бейджей с чужими словами, ?, !, хлопушка, молния, 100, галочка, простые сердца, бокал, наушники, ремень/пряжка, штаны, лонгслив-переворот, сердца с колючкой и кинжалом («под вопросом»), 4 символа v1. Причины по каждому — `REVIEW-v3.md`.

**WARN разобраны:** «Mattes are not officially supported» — по одному inverted matte на эмодзи, рендер в rlottie проверен (факты BRIEF-v2). «Thinner than 28px» (44 cross, 10 key, 21 teddy, сигилы): штрихи логотипа и тату-линии v1; на `sheet-24` читаются. Остальные WARN — см. вывод `qa.py` в разделе ниже отчёта сборки.

**Не проверено:** лимиты custom emoji на core.telegram.org (закрыт прокси). Флаги 🇽 🇹 🇨 у плиток — regional indicator symbols, приём в @Stickers не проверен; фоллбэк ✖️ ➕ ©️ (`upload.md`).
"""


def report():
    """REPORT.md: table in pack order, top-10, cuts, what is left."""
    R = reg()
    sc = {r["file"]: r for r in csv.DictReader(open(os.path.join(HERE, "scores.csv")))}
    names = order("final")
    lines = ["# XTC emoji v3 — отчёт", "",
             f"В паке **{len(names)}** adaptive-эмодзи (TGS 512, 60 fps, 1–3 с). `qa.py`: 0 FAIL; у всех каждый критерий ≥4, плавность/луп 5, Σ≥31, свэг-тест STYLE.md.",
             "Порядок = `manifest.csv` (первый — обложка). Оценки по 7 критериям с обоснованиями — `scores.csv`.", "",
             "| # | файл | 🔣 | история | Σ/35 | KB |", "|---|---|---|---|---|---|"]
    for i, n in enumerate(names, 1):
        e = R[n]
        kb = round(os.path.getsize(os.path.join(HERE, "tgs", n + ".tgs")) / 1024, 1)
        lines.append(f"| {i} | {n} | {e['emoji']} | {e['story']} | {sc[n]['render_sum']} | {kb} |")
    top = sorted(names, key=lambda n: (-int(sc[n]["render_sum"]), n))[:10]
    lines += ["", "## Топ-10", ""] + [f"{i}. **{n}** {R[n]['emoji']}: {sc[n]['render_sum']}/35, {R[n]['story']}" for i, n in enumerate(top, 1)]
    lines += ["", "## Вырезано", "",
              f"v3: вырезано {len(CUT_V3)} из 117 v2 (вердикт и причина по каждому — `REVIEW-v3.md`): "
              + ", ".join(sorted(CUT_V3, key=lambda n: int(n.split("-")[0]))) + ".",
              ""] + [f"- **{n}** {R[n]['emoji']} (v2): {why}" for n, why in CUT_V2.items()]
    lines += ["", V3_MD]
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
