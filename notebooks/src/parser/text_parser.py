import re
from bs4 import BeautifulSoup
from typing import List

from config import ITEM_PATTERN


def contains_item_code(text: str) -> bool:
    """
    Detects SEC Item headers (e.g. Item 7, Item 7A).
    """
    return bool(ITEM_PATTERN.search(text))


def normalize_text(text: str) -> str:
    """
    Normalizes whitespace and SEC-specific artifacts.
    """
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.replace("\xa0", " ").strip()


def extract_text(html: str) -> str:
    """
    Extracts narrative text from HTML with tables/images removed.
    """
    soup = BeautifulSoup(html, "lxml")

    # Remove scripts & styles
    for tag in soup(["script", "style"]):
        tag.decompose()

    # Tables and images should already be removed by their parsers,
    # but this ensures text-only extraction
    for tag in soup(["table", "img"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    return normalize_text(text)
