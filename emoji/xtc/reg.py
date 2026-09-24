"""Pack registry: every spec registers its file name, base emoji, keywords and one-line story."""
REG = {}


def emoji(file, emo, ru, en, story, op=120, series="v1"):
    def deco(fn):
        REG[file] = dict(file=file, fn=fn, emoji=emo, ru=ru, en=en, story=story, op=op, series=series)
        return fn
    return deco
