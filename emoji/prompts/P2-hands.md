# P2: руки, промпты силуэтов для генерации

Кодом в пак вошли пять рук, их силуэт дотянул до шкалы: 👍 126, 👎 127, ✌️ 128, 🤘 129, 👋 130. Для 🙏 🤞 👏 💪 🫶 💅 код не дал силуэта, который читается на 24px, поэтому ниже промпты генерации. Для пяти рук из кода промпты тоже есть, на случай если захочешь их заменить.

## Пайплайн

1. Генерируешь PNG 1024×1024 по промпту (Seedream / Mystic / Nano Banana).
2. Прогоняешь `python3 trace.py hand.png src/NNN-name.svg`. Скрипт вписывает силуэт в 512 с полем 8px и охватом 90%, затем potrace `-s -u 1 -t 20 -O 1.0`.
3. В спеке: `g = geo.svg("src/NNN-name.svg")`. Дальше режешь g на части shapely-пересечениями (пальцы, ладонь) и анимируешь как в `specs/hands.py`.
4. `python3 build.py NNN --view` → `python3 qa.py tgs/` → оценка по шкале.

## Общая часть каждого промпта (вставлять целиком)

> flat solid pure black (#000000) silhouette icon of {ПОЗА}, single shape, bold chunky rounded Y2K sticker style, thick fingers with clear 12px white gaps between fingers, no outline, no inner lines except finger separation gaps, no shading, no gradient, no texture, no text, centered, fills 85% of the frame, pure white background, 1024x1024, vector-like clean edges

Negative: `grey, gradient, shadow, 3d, realistic skin, nails detail, thin lines, outline only, multiple hands, text, watermark, background objects`

## {ПОЗА} по эмодзи

| эмодзи | файл | {ПОЗА} | что анимировать после трассировки |
|---|---|---|---|
| 🙏 | 131-pray | two flat palms pressed together pointing up, seen from the side, wrists at the bottom, slight gap line between the hands | ладони разъезжаются на 6px и схлопываются, ✦ над кончиками |
| 🤞 | 132-fingers-crossed | one hand with index and middle fingers crossed and raised, other fingers folded, thumb over folded fingers | пальцы дрожат (jitter 2f), кулак сжимается «на удачу» |
| 👏 | 133-clap | two open palms facing each other at a slight angle, about to clap, small gap between them | хлопок 3×: slam, ударные линии trim |
| 💪 | 134-muscle | flexed arm bicep, fist up, elbow at bottom left, big round bicep bulge | бицепс раздувается 100→118 с дрожью, ✦ |
| 🫶 | 135-heart-hands | two hands forming a heart shape with thumbs and fingers, heart-shaped hole in the middle | дырка-сердце пульсирует (hole scale), ✦ |
| 💅 | 136-nails | elegant hand with long fingers spread, long pointed nails as separate shapes with gaps, wrist at bottom | ногти по одному «лакируются» глэр-свипом (матт), кисть покачивается |
| 👍 | 126-thumbs-up | fist with thumb up, knuckles facing right | уже в паке (код) |
| 👎 | 127-thumbs-down | fist with thumb down | уже в паке (код) |
| ✌️ | 128-victory | hand with index and middle fingers raised in V, thumb over folded fingers | уже в паке (код) |
| 🤘 | 129-rock | hand with index and pinky raised (rock horns), thumb over folded middle fingers | уже в паке (код) |
| 👋 | 130-wave | open palm, five fingers spread, thumb out to the side | уже в паке (код) |
