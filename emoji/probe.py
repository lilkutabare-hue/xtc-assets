"""BOT_TOKEN=... TG_USER_ID=... python3 probe.py file1.tgs file2.tgs ... -> the server's exact verdict per file (uploadStickerFile)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from upload import call
tok, uid = os.environ["BOT_TOKEN"], os.environ["TG_USER_ID"]
for p in sys.argv[1:]:
    try:
        r = call(tok, "uploadStickerFile", {"user_id": uid, "sticker_format": "animated"}, {"sticker": (os.path.basename(p), open(p, "rb").read())})
        print("OK  ", os.path.basename(p), r.get("file_id", "")[:24])
    except Exception as e:
        print("FAIL", os.path.basename(p), e)
