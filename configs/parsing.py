import re

# ----------------------------
# SEC filing structure
# ----------------------------
SEC_ITEM_MAP = {
    # ───────────── Part I ─────────────
    "Item 1": "Business",
    "Item 1A": "Risk Factors",
    "Item 1B": "Unresolved Staff Comments",
    "Item 1C": "Cybersecurity",
    "Item 2": "Properties",
    "Item 3": "Legal Proceedings",
    "Item 4": "Mine Safety Disclosures",

    # ───────────── Part II ─────────────
    "Item 5": "Market for Registrant’s Common Equity, Related Stockholder Matters and Issuer Purchases of Equity Securities",
    "Item 6": "Reserved",
    "Item 7": "Management’s Discussion and Analysis of Financial Condition and Results of Operations",
    "Item 7A": "Quantitative and Qualitative Disclosures About Market Risk",
    "Item 8": "Financial Statements and Supplementary Data",
    "Item 9": "Changes in and Disagreements with Accountants on Accounting and Financial Disclosure",
    "Item 9A": "Controls and Procedures",
    "Item 9B": "Other Information",

    # ───────────── Part III ─────────────
    "Item 10": "Directors, Executive Officers and Corporate Governance",
    "Item 11": "Executive Compensation",
    "Item 12": "Security Ownership of Certain Beneficial Owners and Management and Related Stockholder Matters",
    "Item 13": "Certain Relationships and Related Transactions, and Director Independence",
    "Item 14": "Principal Accountant Fees and Services",

    # ───────────── Part IV ─────────────
    "Item 15": "Exhibits, Financial Statement Schedules",
}

ITEM_PATTERN = re.compile(r"\bITEM\s*\d+[A-Z]?\s*\.", re.IGNORECASE)

YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")

FINANCIAL_KEYWORDS = {
    "revenue", "net sales", "income", "profit", "loss",
    "assets", "liabilities", "equity", "cash flow",
    "operating", "gross margin", "cost of sales",
    "usd", "dollars", "millions",
}

INLINE_TAGS = {
    "span", "a", "strong", "em", "b", "i", "u",
    "sup", "sub", "small", "font", "mark", "abbr",
}

BLOCK_TAGS = {
    "p", "div", "section", "article",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "li", "blockquote",
}

REMOVE_TAGS = {
    "script", "style", "noscript",
    "header", "footer", "nav", "aside",
}

NON_NARRATIVE_TAGS = {
    "table", "thead", "tbody", "tfoot", "tr", "td", "th",
    "img", "figure", "figcaption",
    "video", "audio", "iframe", "canvas", "svg",
}
