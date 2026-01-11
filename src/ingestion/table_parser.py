import re
from typing import Dict, List
from bs4 import Tag

from configs.parsing import FINANCIAL_KEYWORDS, YEAR_PATTERN, ITEM_PATTERN


def html_table_to_json(table: Tag) -> Dict:
    rows = []
    headers = []

    for i, row in enumerate(table.find_all("tr")):
        cells = [c.get_text(" ", strip=True) for c in row.find_all(["th", "td"])]
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


def classify_table(table_json: Dict) -> str:
    text = f"{table_json.get('headers', [])} {table_json.get('rows', [])}"
    text_lower = text.lower()

    has_years = bool(YEAR_PATTERN.search(text))
    has_numbers = bool(re.search(r"\d{2,}", text))
    has_financial_terms = any(k in text_lower for k in FINANCIAL_KEYWORDS)

    if has_financial_terms and has_years and has_numbers:
        return "financial"
    if has_numbers and any(t in text_lower for t in ["salary", "bonus", "stock", "option"]):
        return "compensation"
    if has_numbers:
        return "entity"
    return "policy"


def process_table(table: Tag, tables_json: List[Dict]) -> None:
    """
    Mutates the DOM in-place.
    """
    # Skip nested/layout tables
    if table.find("table", recursive=False):
        return

    table_text = table.get_text(" ", strip=True)
    table_text = table_text.replace("\xa0", " ")

    # ITEM header tables must stay in narrative
    if ITEM_PATTERN.search(table_text):
        table.replace_with(table_text)
        return

    if len(table_text) < 50:
        table.replace_with(table_text)
        return

    table_json = html_table_to_json(table)
    table_type = classify_table(table_json)

    if table_type in {"financial", "compensation", "entity"}:
        table_json["table_type"] = table_type
        tables_json.append(table_json)
        table.decompose()              # ❌ removed from narrative
    else:
        table.replace_with(table_text) # ✅ preserved in narrative
