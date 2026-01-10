import re
import html
from bs4 import BeautifulSoup, NavigableString, Tag
from config import INLINE_TAGS, BLOCK_TAGS, REMOVE_TAGS, NON_NARRATIVE_TAGS


def normalize_text(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("\u00A0", " ")
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text_from_dom(soup: BeautifulSoup) -> str:
    """
    Extract clean narrative text from SEC / EDGAR HTML.
    Assumes tables & images are already processed separately.
    """

    # 1. Remove non-narrative containers
    for tag in soup.find_all(REMOVE_TAGS | NON_NARRATIVE_TAGS):
        tag.decompose()

    # 2. Unwrap inline tags (CRITICAL for <span>, <sup>, <a>, etc.)
    for tag in soup.find_all(INLINE_TAGS):
        tag.unwrap()

    paragraphs = []
    buffer = []

    def flush_buffer():
        if buffer:
            paragraphs.append(" ".join(buffer).strip())
            buffer.clear()

    root = soup.body if soup.body else soup

    for node in root.descendants:
        # --- Orphan text node ---
        if isinstance(node, NavigableString):
            text = str(node).strip()
            if text:
                buffer.append(text)

        # --- Block-level tag boundary ---
        elif isinstance(node, Tag) and node.name in BLOCK_TAGS:
            flush_buffer()

    flush_buffer()

    return normalize_text("\n\n".join(paragraphs))
