import re
from typing import Optional

def normalize_item_code(match) -> Optional[str]:
    """
    Normalize a regex match into a canonical SEC item code.

    Returns values compatible with SEC_ITEM_MAP:
    e.g. 'Item 1', 'Item 1A', 'Item 7A', 'Item 15'

    Returns None if the match is invalid or unsupported.
    """

    if match is None:
        return None

    # Prefer captured group if available
    raw = match.group(1) if match.lastindex else match.group(0)
    raw = raw.upper().strip()

    # Remove trailing punctuation
    raw = re.sub(r"[.:]\s*$", "", raw)

    # Normalize whitespace
    raw = re.sub(r"\s+", " ", raw)

    # Ensure prefix
    if not raw.startswith("ITEM "):
        raw = re.sub(r"^ITEM\s*", "ITEM ", raw)

    # Validate format strictly
    m = re.fullmatch(r"ITEM (\d{1,2})([A-Z]?)", raw)
    if not m:
        return None

    number, letter = m.groups()
    return f"Item {number}{letter}"
