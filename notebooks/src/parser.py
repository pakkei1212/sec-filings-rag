import os
import re
import hashlib
from typing import List, Dict, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from config_bak import (
    IMAGES_DIR,
    FINANCIAL_KEYWORDS,
    YEAR_PATTERN,
    ITEM_PATTERN,   # ✅ added
)

# ----------------------------
# Table utilities
# ----------------------------
def html_table_to_json(table) -> Dict:
    """
    Converts an HTML <table> into structured JSON
    suitable for LLMs or downstream querying.
    """
    rows = []
    headers = []

    for i, row in enumerate(table.find_all("tr")):
        cells = [c.get_text(strip=True) for c in row.find_all(["th", "td"])]

        if not cells:
            continue

        if i == 0:
            headers = cells
        else:
            if headers and len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
            else:
                rows.append({"row": cells})

    return {
        "type": "table",
        "headers": headers,
        "rows": rows,
    }


# ----------------------------
# Table classification
# ----------------------------
def classify_table(table_json: Dict) -> str:
    """
    Classifies SEC tables into semantic categories.
    """
    headers_text = table_json.get("headers", [])
    rows_text = table_json.get("rows", [])

    text = f"{headers_text} {rows_text}"
    text_lower = text.lower()

    has_years = bool(YEAR_PATTERN.search(text))
    has_numbers = bool(re.search(r"\d{2,}", text))
    has_financial_terms = any(k in text_lower for k in FINANCIAL_KEYWORDS)

    if has_financial_terms and has_years and has_numbers:
        return "financial"

    if has_numbers and any(t in text_lower for t in ["salary", "bonus", "stock", "option"]):
        return "compensation"

    if has_numbers and not has_financial_terms:
        return "entity"

    if not has_numbers:
        return "policy"

    return "unknown"


# ----------------------------
# Text helpers
# ----------------------------
ITEM_PATTERN = re.compile(
    r"\bITEM\s+\d+[A-Z]?\b",
    re.IGNORECASE
)

def contains_item_code(text: str) -> bool:
    return bool(ITEM_PATTERN.search(text))


def normalize_text(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.replace("\xa0", " ").strip()


# ----------------------------
# Main extraction
# ----------------------------
def extract_text_tables_images(
    html: str,
    base_url: str,
) -> Tuple[str, List[Dict], List[Dict]]:
    """
    Extracts:
    - narrative text
    - structured tables
    - image metadata (no downloading)
    """
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    soup = BeautifulSoup(html, "lxml")

    # 1️⃣ Remove scripts & styles
    for tag in soup(["script", "style"]):
        tag.decompose()

    # 2️⃣ Extract images (metadata only)
    images = []

    for img in soup.find_all("img"):
        src = img.get("src")
        if not src:
            continue

        img_url = urljoin(base_url, src)
        img_id = hashlib.md5(img_url.encode()).hexdigest()
        ext = os.path.splitext(img_url)[1].split("?")[0] or ".png"

        images.append({
            "image_id": img_id,
            "image_url": img_url,
            "image_path": str(IMAGES_DIR / f"{img_id}{ext}"),
            "alt_text": img.get("alt", "").strip()
        })

        img.decompose()

    # 3️⃣ Extract tables
    tables_json = []

    for table in soup.find_all("table"):

        if table.find("table"):
            continue

        table_text = table.get_text(" ", strip=True)

        if contains_item_code(table_text) or len(table_text) < 50:
            table.replace_with(table_text)
            continue

        table_json = html_table_to_json(table)
        table_type = classify_table(table_json)

        if table_type in {"financial", "compensation", "entity"}:
            tables_json.append(table_json)
            table.decompose()
        else:
            table.replace_with(table_text)

    # 4️⃣ Extract narrative text
    text = soup.get_text(separator="\n")
    text = normalize_text(text)

    return text, tables_json, images
