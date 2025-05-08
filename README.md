# OCR Batch Script for SanskritDictionary.com

## Overview

This repository provides a Python script (`batch_ocr.py`) to perform batch OCR on a directory of images by leveraging the OCR functionality of [ocr.sanskritdictionary.com](https://ocr.sanskritdictionary.com/). The script uploads each image to the site's `/recognise` endpoint, retrieves the extracted text (Sanskrit and/or English), cleans up HTML tags, and saves the results as plain-text `.txt` files.

## Features

* Automates the upload of multiple image files (`.png`, `.jpg`, etc.).
* Retrieves OCR results in Sanskrit (`lang=san`) using Google OCR engine.
* Cleans `<br />` HTML tags and converts them to real line breaks.
* Saves one `.txt` file per image in a designated output folder.
* Configurable delay between requests to avoid overwhelming the server.
* Uses `requests` and `certifi` for secure HTTP requests.

## Prerequisites

* Python 3.6 or higher
* Git (for cloning the repository)
* Internet connection
* [Requests](https://pypi.org/project/requests/) library
* [Certifi](https://pypi.org/project/certifi/) library

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/ocr-batch.git
   cd ocr-batch
   ```

2. Create and activate a Python virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   *(Or install individually: `pip install requests certifi`)*

## Configuration

* Place all the images you want to OCR in the `images/` directory.
* Ensure the `results/` directory exists—it will be auto-created if missing.
* Open the script `batch_ocr.py` to adjust:

  * `PAYLOAD` for language options (`"lang": "san"`, `"service": "google"`)
  * `DELAY_SECONDS` for pause time between requests.
  * `FILE_FIELD` if the form field name changes.

## Usage

Run the script:

```bash
python batch_ocr.py
```

You will see progress messages and, upon completion, one `.txt` file per image in the `results/` directory.

## Folder Structure

```
ocr-batch/
├── batch_ocr.py      # Main OCR script
├── images/           # Input images for OCR
├── results/          # Output text files (created automatically)
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Example

```bash
⏳ OCR’ing image1.png… ✅ Saved → results/image1.txt
⏳ OCR’ing image2.jpg… ✅ Saved → results/image2.txt
🎉 All done!
```

## Troubleshooting

* **SSL Errors**: Ensure certifi is installed; the script uses `certifi.where()` for CA bundle.
* **HTTP 403/503**: Increase `DELAY_SECONDS` or verify the form fields and headers match the site's network requests.
* **Encoding issues**: Script uses ASCII-only headers and UTF-8 for outputs.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Contributing

Feel free to open issues or submit pull requests!

---
