"""Apply the three rlottie format fixes to v1 files (for calibration only, not part of the pack)."""
import glob, gzip, json, os, sys

def fix(o):
    if isinstance(o, dict):
        if o.get("a") == 1 and isinstance(o.get("k"), list):
            ks = o["k"]
            for k in ks[:-1]:
                if isinstance(k, dict) and not k.get("h"):
                    k.setdefault("o", {"x": [0.42], "y": [0]})
                    k.setdefault("i", {"x": [0.58], "y": [1]})
            if ks and isinstance(ks[-1], dict):
                ks[-1] = {"t": ks[-1]["t"], "s": ks[-1].get("s", ks[-2].get("e") if len(ks) > 1 else None)}
        for v in o.values():
            fix(v)
    elif isinstance(o, list):
        for v in o:
            fix(v)

src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
for p in sorted(glob.glob(os.path.join(src, "*.tgs"))):
    d = json.load(gzip.open(p))
    for L in d["layers"]:
        for key in ("o", "r"):
            pr = L["ks"].get(key)
            if pr and pr.get("a") == 0 and isinstance(pr.get("k"), list):
                pr["k"] = pr["k"][0]
        fix(L)
    with gzip.open(os.path.join(dst, os.path.basename(p)), "wt") as f:
        json.dump(d, f, separators=(",", ":"))
