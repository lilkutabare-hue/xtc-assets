"""Lottie writer for Telegram adaptive emoji.

Every animated property is written by `Track`, which enforces the three rlottie rules
(see qa.py): static o/r are scalars, every key but the last has both `i` and `o`,
and the last key is only `t` + `s`.
"""
import gzip
import json
import math

FPS = 60
BLACK = [0, 0, 0, 1]

# cubic-bezier presets (x1, y1, x2, y2) — the curve from a key to the next one
EASE = {
    "lin": (0.0, 0.0, 1.0, 1.0),
    "io": (0.37, 0.0, 0.63, 1.0),      # sine in-out: pose to pose
    "io3": (0.65, 0.0, 0.35, 1.0),     # cubic in-out: heavier, snappier middle
    "io5": (0.83, 0.0, 0.17, 1.0),     # quint in-out: whip
    "o": (0.33, 1.0, 0.68, 1.0),       # cubic out
    "o5": (0.22, 1.0, 0.36, 1.0),      # quint out: hit and glide
    "ox": (0.16, 1.0, 0.3, 1.0),       # expo out: pop
    "os": (0.61, 1.0, 0.88, 1.0),      # sine out
    "i": (0.32, 0.0, 0.67, 0.0),       # cubic in
    "i5": (0.64, 0.0, 0.78, 0.0),      # quint in: gravity / wind-up
    "is": (0.12, 0.0, 0.39, 0.0),      # sine in
    "back": (0.34, 1.56, 0.64, 1.0),   # out-back overshoot
    "antic": (0.36, 0.0, 0.66, -0.56),  # in-back: pull back before going
    # measured in official Telegram files (moodboard.md, "Числа")
    "easy": (0.33, 0.0, 0.67, 1.0),    # EASY_EASE
    "swift": (0.3, 0.0, 0.4, 1.0),     # hammer wind-up, tears
    "swing": (0.3, 0.0, 0.7, 1.0),     # 10f oscillations
    "decel": (0.17, 0.17, 0.34, 1.0),  # linear start, brake (ball up, jaw opens)
    "slam": (0.66, 0.0, 0.83, 0.83),   # accelerate into contact (ball down, jaw shuts)
    "strike": (0.6, 0.0, 0.85, 1.0),   # hammer strike
    "snap": (0.1, 0.0, 0.4, 1.0),      # SNAP_IN pop
    "snapo": (0.3, 0.0, 0.1, 1.0),     # SNAP_OUT tear launch
    "ring": (0.05, 0.0, 0.3, 1.0),     # shock ring
    "aelin": (0.167, 0.167, 0.833, 0.833),
}


def _r(x, nd=2):
    if isinstance(x, (list, tuple)):
        return [_r(v, nd) for v in x]
    if isinstance(x, float):
        x = round(x, nd)
        if x == int(x):
            return int(x)
    return x


def ease_of(e):
    if isinstance(e, str):
        return EASE[e]
    return tuple(e)


class Track:
    """Pose-to-pose keyframes. `to(t, v, ease)` sets the curve of the segment that ends at t."""

    def __init__(self, v, t=0):
        self.k = [[t, v, None]]

    @property
    def v(self):
        return self.k[-1][1]

    @property
    def t(self):
        return self.k[-1][0]

    @property
    def v0(self):
        return self.k[0][1]

    def to(self, t, v, ease="io"):
        if t <= self.t + 1e-6:
            raise ValueError(f"key time {t} not after {self.t}")
        self.k[-1][2] = ease
        self.k.append([t, v, None])
        return self

    def by(self, dt, v, ease="io"):
        return self.to(self.t + dt, v, ease)

    def hold(self, t):
        if t > self.t + 1e-6:
            self.to(t, self.v, "lin")
        return self

    def wait(self, dt):
        return self.hold(self.t + dt)

    def loop(self, op, ease="io"):
        """Close the loop: value at op == value at 0."""
        if abs(self.t - op) < 1e-6:
            if self.v != self.v0:
                raise ValueError("track ends at op with a value that does not close the loop")
            return self
        return self.to(op, self.v0, ease)

    def at(self, t):
        """Evaluate (for tooling: bbox, particle attachment)."""
        k = self.k
        if t <= k[0][0]:
            return k[0][1]
        for (t0, v0, e), (t1, v1, _) in zip(k, k[1:]):
            if t0 <= t <= t1:
                u = bez_y(ease_of(e), (t - t0) / (t1 - t0))
                if isinstance(v0, (list, tuple)):
                    return [a + (b - a) * u for a, b in zip(v0, v1)]
                return v0 + (v1 - v0) * u
        return k[-1][1]

    def shifted(self, dt):
        t = Track(self.k[0][1], self.k[0][0] + dt)
        t.k = [[a + dt, b, c] for a, b, c in self.k]
        return t

    def json(self, shape=False):
        if len(self.k) == 1:
            return static(self.k[0][1])
        out = []
        n = len(self.k)
        for i, (t, v, e) in enumerate(self.k):
            key = {"t": _r(float(t))}
            if shape:
                key["s"] = [v]
            else:
                key["s"] = _r(list(v)) if isinstance(v, (list, tuple)) else [_r(float(v))]
            if i < n - 1:
                if e == "hold":
                    key["h"] = 1
                else:
                    x1, y1, x2, y2 = ease_of(e)
                    key["o"] = {"x": [x1], "y": [y1]}
                    key["i"] = {"x": [x2], "y": [y2]}
            out.append(key)
        return {"a": 1, "k": out}


def bez_y(e, x):
    """y of a cubic-bezier easing at progress x (Newton on x)."""
    x1, y1, x2, y2 = e

    def bx(s):
        return 3 * (1 - s) ** 2 * s * x1 + 3 * (1 - s) * s * s * x2 + s ** 3

    def by(s):
        return 3 * (1 - s) ** 2 * s * y1 + 3 * (1 - s) * s * s * y2 + s ** 3

    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if bx(mid) < x:
            lo = mid
        else:
            hi = mid
    return by((lo + hi) / 2)


def static(v):
    if isinstance(v, (list, tuple)):
        return {"a": 0, "k": _r(list(v))}
    return {"a": 0, "k": _r(float(v))}


class Split:
    """Position with separate X/Y tracks (lets X and Y have different curves: true arcs)."""

    def __init__(self, x, y):
        self.x, self.y = x, y

    @property
    def v0(self):
        return [self.x.v0 if isinstance(self.x, Track) else self.x, self.y.v0 if isinstance(self.y, Track) else self.y]

    def at(self, t):
        return [self.x.at(t) if isinstance(self.x, Track) else self.x, self.y.at(t) if isinstance(self.y, Track) else self.y]


def prop(v, shape=False):
    if isinstance(v, Split):
        return {"s": True, "x": prop(v.x), "y": prop(v.y)}
    if isinstance(v, Track):
        return v.json(shape)
    if isinstance(v, dict) and "a" in v:
        return v
    if shape:
        return {"a": 0, "k": v}
    return static(v)


def fit(fn, times, dim=None):
    """Hermite -> bezier keys for a smooth 1D function sampled at `times` (monotonic segments!).
    Put keys at extrema of fn so every segment has a non-zero value change."""
    eps = 0.05
    tr = Track(fn(times[0]), times[0])
    vals = [fn(t) for t in times]
    der = [(fn(t + eps) - fn(t - eps)) / (2 * eps) for t in times]
    for i in range(len(times) - 1):
        t0, t1 = times[i], times[i + 1]
        v0, v1 = vals[i], vals[i + 1]
        dt, dv = t1 - t0, v1 - v0
        if abs(dv) < 1e-6:
            e = (0.33, 0.0, 0.67, 1.0)
        else:
            y1 = der[i] * dt / 3 / dv
            y2 = 1 - der[i + 1] * dt / 3 / dv
            e = (1 / 3, round(y1, 4), 2 / 3, round(y2, 4))
        tr.to(t1, v1, e)
    return tr


# ---------------------------------------------------------------- shapes


def fill(o=100, evenodd=True):
    return {"ty": "fl", "c": static(BLACK), "o": prop(o), "r": 2 if evenodd else 1, "nm": "fill"}


def stroke(w, o=100, cap=2, join=2):
    return {"ty": "st", "c": static(BLACK), "o": prop(o), "w": prop(w), "lc": cap, "lj": join, "ml": 4, "nm": "stroke"}


def trim(s=0, e=100, o=0):
    return {"ty": "tm", "s": prop(s), "e": prop(e), "o": prop(o), "m": 1, "nm": "trim"}


def tr(p=(0, 0), a=(0, 0), s=(100, 100), r=0, o=100):
    return {"ty": "tr", "p": prop(p), "a": prop(a), "s": prop(s), "r": prop(r), "o": prop(o),
            "sk": static(0), "sa": static(0)}


def group(items, nm="g", **t):
    return {"ty": "gr", "nm": nm, "it": list(items) + [tr(**t)]}


def pathdata(pts, closed=True, ins=None, outs=None):
    n = len(pts)
    return {"c": closed, "v": _r([list(p) for p in pts], 1),
            "i": _r([list(p) for p in ins], 1) if ins else [[0, 0]] * n,
            "o": _r([list(p) for p in outs], 1) if outs else [[0, 0]] * n}


def sh(data, nm="p"):
    """data: pathdata dict or a Track of pathdata dicts (shape morph)."""
    return {"ty": "sh", "nm": nm, "ks": prop(data, shape=True)}


# ---------------------------------------------------------------- layers


class Layer:
    def __init__(self, comp, ind, nm, ty, shapes, parent, p, a, s, r, o, ip, op):
        self.comp, self.ind, self.nm, self.ty = comp, ind, nm, ty
        self.shapes, self.parent = shapes, parent
        self.p, self.a, self.s, self.r, self.o = p, a, s, r, o
        self.ip, self.op = ip, op
        self.matte = None  # 'alpha' | 'inv'
        self.is_matte = False

    def json(self):
        d = {"ddd": 0, "ind": self.ind, "ty": self.ty, "nm": self.nm, "sr": 1,
             "ks": {"o": prop(self.o), "r": prop(self.r), "p": prop(self.p), "a": prop(self.a), "s": prop(self.s)},
             "ao": 0, "ip": self.ip, "op": self.op, "st": 0, "bm": 0}
        if self.parent is not None:
            d["parent"] = self.parent.ind
        if self.ty == 4:
            d["shapes"] = self.shapes
        if self.is_matte:
            d["td"] = 1
        if self.matte:
            d["tt"] = 1 if self.matte == "alpha" else 2
        return d


class Comp:
    """Layers are added bottom-to-top (painter's order)."""

    def __init__(self, name, op=120):
        self.name, self.op = name, op
        self.layers = []

    def _add(self, nm, ty, shapes, parent, p, a, s, r, o, ip, op):
        l = Layer(self, len(self.layers) + 1, nm, ty, shapes, parent, p, a, s, r, o,
                  ip, self.op if op is None else op)
        self.layers.append(l)
        return l

    def layer(self, nm, shapes, parent=None, p=(256, 256), a=None, s=(100, 100), r=0, o=100, ip=0, op=None):
        if a is None:
            a = p if not isinstance(p, (Track, Split)) else p.v0
        return self._add(nm, 4, shapes, parent, p, a, s, r, o, ip, op)

    def null(self, nm, parent=None, p=(256, 256), a=None, s=(100, 100), r=0, o=100, ip=0, op=None):
        if a is None:
            a = p if not isinstance(p, (Track, Split)) else p.v0
        return self._add(nm, 3, None, parent, p, a, s, r, o, ip, op)

    def matte(self, target, nm, shapes, mode="inv", **kw):
        """Track matte for `target` (inv = shapes cut holes through it). Max ONE per emoji (brief).
        The matte layer lives for the whole comp; park it off the art when idle."""
        if any(l.is_matte for l in self.layers):
            raise ValueError("only one matte per emoji")
        l = self.layer(nm, shapes, **kw)
        self.layers.remove(l)
        self.layers.insert(self.layers.index(target) + 1, l)
        l.is_matte = True
        l.ip, l.op = 0, self.op
        target.matte = "alpha" if mode == "alpha" else "inv"
        return l

    def json(self):
        layers = [l.json() for l in reversed(self.layers)]
        # a matte (td) must be directly above its target in the array
        return {"v": "5.5.7", "fr": FPS, "ip": 0, "op": self.op, "w": 512, "h": 512, "nm": self.name,
                "ddd": 0, "assets": [], "layers": layers}

    def save(self, path):
        data = json.dumps(self.json(), separators=(",", ":"))
        with open(path, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", compresslevel=9, mtime=0) as f:
            f.write(data.encode())       # mtime=0: identical input -> identical .tgs (clean git diffs)
        return path
