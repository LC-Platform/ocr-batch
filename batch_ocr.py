# batch_ocr.py

import os
import time
import requests
import certifi
from mimetypes import guess_type

# ─── Configuration ────────────────────────────────────────────────
BASE_URL   = "https://ocr.sanskritdictionary.com/"
OCR_URL    = BASE_URL + "recognise"

PAYLOAD    = {
    "lang":    "san",    # Sanskrit
    "service": "google", # Google OCR engine
}
FILE_FIELD = "image"

# ─── Session setup ────────────────────────────────────────────────
session = requests.Session()
# use certifi’s CA bundle to avoid SSL errors
session.verify = certifi.where()
session.headers.update({
    "User-Agent":       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/135.0.0.0 Safari/537.36",
    "Accept":           "*/*",
    "Accept-Language":  "en-US,en;q=0.9,hi;q=0.8",
    "Referer":          BASE_URL,
    "Origin":           BASE_URL,
    "X-Requested-With": "XMLHttpRequest",
})

# prime cookies
try:
    session.get(BASE_URL, timeout=10).raise_for_status()
except requests.HTTPError as e:
    print(f"⚠️  Initial GET returned {e}. Continuing without cookies…")

# ─── Paths ───────────────────────────────────────────────────────
CWD        = os.getcwd()
IMAGE_DIR  = os.path.join(CWD, "images")
OUTPUT_DIR = os.path.join(CWD, "results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Batch OCR ───────────────────────────────────────────────────
for fname in sorted(os.listdir(IMAGE_DIR)):
    if not fname.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".tif", ".bmp")):
        continue

    path = os.path.join(IMAGE_DIR, fname)
    mime = guess_type(path)[0] or "application/octet-stream"

    print(f"⏳ OCR’ing {fname}…", end=" ")

    # upload
    with open(path, "rb") as f:
        files = { FILE_FIELD: (fname, f, mime) }
        r = session.post(OCR_URL, data=PAYLOAD, files=files, timeout=60)

    if r.status_code == 200:
        # parse JSON
        data = r.json()
        html = data.get("text", "")

        # clean up HTML line breaks
        clean = html.replace("\r", "").replace("<br />", "\n").strip()

        # save to .txt
        out_path = os.path.join(OUTPUT_DIR, f"{os.path.splitext(fname)[0]}.txt")
        with open(out_path, "w", encoding="utf-8") as out:
            out.write(clean)

        print(f"✅ Saved → {out_path}")
    else:
        print(f"❌ HTTP {r.status_code}")

    # polite pause
    time.sleep(2)

print("🎉 All done!")
