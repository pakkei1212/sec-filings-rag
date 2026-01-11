import os
import hashlib
from typing import List, Dict
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from config_bak import IMAGES_DIR


def extract_images(html: str, base_url: str) -> List[Dict]:
    """
    Extracts image metadata only (no downloading).
    """
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    soup = BeautifulSoup(html, "lxml")

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

    return images
