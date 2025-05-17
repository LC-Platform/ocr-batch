# batch_ocr.py

import os
import re
import time
import glob
import shutil
import requests
import certifi
from mimetypes import guess_type
from bs4 import BeautifulSoup

# ─── Configuration ────────────────────────────────────────────────
BASE_URL      = "https://ocr.sanskritdictionary.com/"
OCR_URL       = BASE_URL + "recognise"
PAYLOAD       = {"lang": "san", "service": "google"}
FILE_FIELD    = "image"
DELAY_SECONDS = 5      # seconds between pages
MAX_RETRIES   = 3      # per page
RETRY_DELAY   = 5      # seconds between retry attempts

# ─── Session setup ────────────────────────────────────────────────
session = requests.Session()
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
# attempt to pick up cookies (ignore errors)
try:
    session.get(BASE_URL, timeout=10)
except Exception:
    pass

# ─── Paths ───────────────────────────────────────────────────────
CWD        = os.getcwd()
IMAGE_DIR  = os.path.join(CWD, "images")
OUTPUT_DIR = os.path.join(CWD, "results")
FAILED_DIR = os.path.join(CWD, "failed")
for d in (OUTPUT_DIR, FAILED_DIR):
    os.makedirs(d, exist_ok=True)

# ─── Helper to extract page number for sorting ───────────────────
def page_number(path):
    m = re.search(r"page_(\d+)", os.path.basename(path))
    return int(m.group(1)) if m else 0

# ─── Gather & sort files ────────────────────────────────────────
files = sorted(
    glob.glob(os.path.join(IMAGE_DIR, "page_*.*")),
    key=page_number
)

combined_pages = []   # will hold (page_no, text)
failed_pages   = []   # will hold (page_no, filename)

# ─── OCR loop with retries and failure handling ───────────────────
for path in files:
    fname = os.path.basename(path)
    pg = page_number(path)
    mime = guess_type(path)[0] or "application/octet-stream"
    ocr_text = ""

    print(f"\n⏳ Processing {fname} (page {pg})…")

    # Retry loop
    for attempt in range(1, MAX_RETRIES + 1):
        with open(path, "rb") as f:
            files_dict = { FILE_FIELD: (fname, f, mime) }
            resp = session.post(OCR_URL, data=PAYLOAD, files=files_dict, timeout=60)

        if resp.status_code != 200:
            print(f"  ⚠️ Attempt {attempt}: HTTP {resp.status_code}")
        else:
            # JSON extraction
            try:
                data = resp.json()
                ocr_text = data.get("text", "").strip()
            except Exception:
                ocr_text = ""
            # Fallback HTML extraction if empty
            if not ocr_text:
                soup = BeautifulSoup(resp.text, "html.parser")
                container = soup.find(id="result") or soup.find("textarea") or soup
                ocr_text = container.get_text("\n", strip=True).strip()

        # Clean up HTML breaks
        clean = ocr_text.replace("\r", "").replace("<br />", "\n").strip()

        # Detect failure message
        if not clean or clean.lower().startswith("recognition failed"):
            print(f"  ❌ Attempt {attempt}: no valid text extracted")
            ocr_text = ""
            if attempt < MAX_RETRIES:
                print(f"  ↩️ Retrying in {RETRY_DELAY}s…")
                time.sleep(RETRY_DELAY)
            continue
        else:
            print(f"  ✅ Success on attempt {attempt}")
            combined_pages.append((pg, clean))
            break

    # If after retries, still no text
    if not ocr_text:
        print(f"  🚨 Recognition failed after {MAX_RETRIES} attempts")
        failed_pages.append((pg, fname))
        shutil.copy(path, os.path.join(FAILED_DIR, fname))
        print(f"  📂 Moved failed image to {FAILED_DIR}")

    print(f"⏱ Waiting {DELAY_SECONDS}s before next…")
    time.sleep(DELAY_SECONDS)

# ─── Write combined output ────────────────────────────────────────
if combined_pages:
    combined_pages.sort(key=lambda x: x[0])
    out_file = os.path.join(OUTPUT_DIR, "all_pages.txt")
    with open(out_file, "w", encoding="utf-8") as out:
        for pg, text in combined_pages:
            out.write(f"=== Page {pg} ===\n{text}\n\n")
    print(f"\n🎉 All done! Combined text saved to {out_file}")
else:
    print("\n⚠️ No pages were successfully recognized.")

# ─── Summary of failures ─────────────────────────────────────────
if failed_pages:
    failed_list = [f"page_{pg} ({fname})" for pg, fname in failed_pages]
    print(f"\n❌ Pages that failed OCR and were moved to 'failed/': {failed_list}")
