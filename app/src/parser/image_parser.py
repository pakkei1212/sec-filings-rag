import os
import hashlib
import requests

from typing import List, Dict
from urllib.parse import urljoin, urlparse
from bs4 import Tag

from src.embedding_manager_transformer import TransformerEmbeddingManager
from src.utils.sec_items import normalize_item_code
from config import IMAGES_DIR, SEC_HEADERS, ITEM_PATTERN

def normalize_vision_output(text: str) -> str:
    """
    Normalize vision model output to a canonical decision.
    """
    if not text:
        return ""

    t = text.strip().lower()

    # Hard decision
    if "non_informative_image" in t:
        return "NON_INFORMATIVE_IMAGE"

    # Strong logo / branding signals
    logo_signals = [
        "logo",
        "branding",
        "trademark",
        "stylized apple",
        "company logo",
        "non-informative image",
    ]

    if any(s in t for s in logo_signals):
        return "NON_INFORMATIVE_IMAGE"

    return text.strip()

def process_images(
        soup,
        base_url: str,
        embedding_manager: TransformerEmbeddingManager,
    ) -> List[Dict]:
    """
    Extracts image metadata and removes images from DOM.
    """
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    images: List[Dict] = []

    current_item = None

    for elem in soup.descendants:
        if isinstance(elem, Tag):
            text = elem.get_text(" ", strip=True)
            if text:
                m = ITEM_PATTERN.search(text)
                if m:
                    current_item = normalize_item_code(m)

        # ---- Process images ----
        if isinstance(elem, Tag) and elem.name == "img":
            src = elem.get("src")
            if not src:
                elem.decompose()
                continue

            # ---- Remote URL ----
            img_url = urljoin(base_url, src)

            # ---- Stable local filename ----
            img_id = hashlib.md5(img_url.encode()).hexdigest()
            ext = os.path.splitext(urlparse(img_url).path)[1] or ".png"
            img_path = IMAGES_DIR / f"{img_id}{ext}"

            # ---- Download if missing ----
            if not img_path.exists():
                try:
                    r = requests.get(
                        img_url,
                        timeout=15,
                        headers=SEC_HEADERS,
                    )
                    r.raise_for_status()

                    with open(img_path, "wb") as f:
                        f.write(r.content)

                except Exception as e:
                    # Skip image if download fails
                    elem.decompose()
                    continue

            # ---- Generate SEC-aware image description ----
            raw_description = embedding_manager.generate_image_description(str(img_path))
            description = normalize_vision_output(raw_description)

            # ---- Skip non-informative images (logos, decorations) ----
            if not description or description.strip() == "NON_INFORMATIVE_IMAGE":
                elem.decompose()
                continue

            # ---- Record metadata ----
            images.append({
                "image_id": img_id,
                "image_url": img_url,
                "image_path": str(img_path),
                "alt_text": elem.get("alt", ""),
                "image_description": description,
                "item_code": current_item,   # ⭐ KEY PART
            })

            # ---- Remove image from DOM ----
            elem.decompose()

    return images
