#!/usr/bin/env python3
"""Upload the pack as an adaptive custom-emoji set through the Bot API (no dependencies).

  BOT_TOKEN=123:abc TG_USER_ID=12345 python3 upload.py xtc_emoji "XTC emoji" [manifest.csv]

- set name gets the mandatory suffix `_by_<bot_username>` (Telegram rule for bot-created sets);
- needs_repainting=true -> adaptive: the emoji takes the text colour (only alpha matters);
- first 50 stickers go in createNewStickerSet, the rest one by one with addStickerToSet;
- order = manifest order (the first one is the pack's cover).
Re-running with an existing set name skips the create call and appends what is missing.
"""
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://api.telegram.org/bot{}/{}"


def call(token, method, fields=None, files=None):
    boundary = uuid.uuid4().hex
    body = bytearray()
    for k, v in (fields or {}).items():
        body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
    for k, (fname, data) in (files or {}).items():
        body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{fname}\"\r\n"
                 f"Content-Type: application/x-tgsticker\r\n\r\n").encode() + data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    req = urllib.request.Request(API.format(token, method), data=bytes(body),
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                res = json.load(r)
        except urllib.error.HTTPError as e:
            res = json.load(e)
        if res.get("ok"):
            return res["result"]
        retry = res.get("parameters", {}).get("retry_after")
        if retry:
            time.sleep(retry + 1)
            continue
        raise RuntimeError(f"{method}: {res.get('description')}")
    raise RuntimeError(f"{method}: gave up after retries")


def keywords(ru, en, limit=64):
    """Bot API: up to 20 keywords, total length <= 64 chars. Interleave ru/en by priority."""
    ru = [k.strip() for k in ru.split(",") if k.strip()]
    en = [k.strip() for k in en.split(",") if k.strip()]
    out, total = [], 0
    for pair in zip(ru + [""] * len(en), en + [""] * len(ru)):
        for k in pair:
            if k and k not in out and total + len(k) <= limit and len(out) < 20:
                out.append(k)
                total += len(k)
    return out


def sticker(row, name):
    return {"sticker": f"attach://{name}", "format": "animated", "emoji_list": [row["emoji"]],
            "keywords": keywords(row["keywords_ru"], row["keywords_en"])}


def main():
    token, user = os.environ["BOT_TOKEN"], int(os.environ["TG_USER_ID"])
    short, title = sys.argv[1], sys.argv[2]
    rows = list(csv.DictReader(open(sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "manifest.csv"))))
    me = call(token, "getMe")
    name = f"{short}_by_{me['username']}"
    try:
        existing = call(token, "getStickerSet", {"name": name})
        done = len(existing["stickers"])
        print(f"set exists with {done} emoji, appending")
    except RuntimeError:
        first = rows[:50]
        files = {f"f{i}": (r["file"], open(os.path.join(HERE, "tgs", r["file"]), "rb").read()) for i, r in enumerate(first)}
        call(token, "createNewStickerSet", {
            "user_id": user, "name": name, "title": title, "sticker_type": "custom_emoji",
            "needs_repainting": "true",
            "stickers": json.dumps([sticker(r, f"f{i}") for i, r in enumerate(first)], ensure_ascii=False)}, files)
        done = len(first)
        print(f"created {name} with {done}")
    for r in rows[done:]:
        data = open(os.path.join(HERE, "tgs", r["file"]), "rb").read()
        call(token, "addStickerToSet", {"user_id": user, "name": name,
                                        "sticker": json.dumps(sticker(r, "f0"), ensure_ascii=False)},
             {"f0": (r["file"], data)})
        print("+", r["file"])
    print(f"https://t.me/addemoji/{name}")


if __name__ == "__main__":
    main()
