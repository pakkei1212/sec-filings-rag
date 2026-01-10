import os
import re
from pathlib import Path

# ----------------------------
# Base directories
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
CACHE_DIR = BASE_DIR / "cache"

for d in [DATA_DIR, OUTPUT_DIR, CACHE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ----------------------------
# Environment / API settings
# ----------------------------
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "YourName your@email.com")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ----------------------------
# Model configuration
# ----------------------------
MODEL_NAME = "Qwen/Qwen2.5-VL-3B-Instruct"

MODEL_CACHE_DIR = CACHE_DIR / "models"
MODEL_CACHE_DIR.mkdir(exist_ok=True)

# ----------------------------
# Vector database (Chroma)
# ----------------------------
CHROMA_PERSIST_DIR = os.getenv(
    "CHROMA_PERSIST_DIR",
    "/workspace/data/chroma"
)
CHROMA_DIR = Path(CHROMA_PERSIST_DIR)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# Backward compatibility / alias
VECTOR_DB_PATH = CHROMA_DIR

# ----------------------------
# Ollama configuration
# ----------------------------
OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://ollama:11434/"
)

BATCH_SIZE = int(os.getenv("BATCH_SIZE", 128))

# ----------------------------
# SEC data endpoints
# ----------------------------
BASE_DATA = "https://data.sec.gov"
BASE_ARCHIVE = "https://www.sec.gov"

SUBMISSIONS_DIR = Path(
    os.getenv("SUBMISSIONS_DIR", "/workspace/data/submissions")
)
IMAGES_DIR = Path(
    os.getenv("IMAGES_DIR", "/workspace/data/sec_images")
)

for d in [SUBMISSIONS_DIR, IMAGES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ----------------------------
# SEC filing structure
# ----------------------------
SEC_ITEM_MAP = {
    # ───────────── Part I ─────────────
    "Item 1": "Business",
    "Item 1A": "Risk Factors",
    "Item 1B": "Unresolved Staff Comments",
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

# ----------------------------
# SEC parsing patterns
# ----------------------------
ITEM_PATTERN = re.compile(
    r"\bITEM\s+\d+[A-Z]?\b",
    re.IGNORECASE
)

# ----------------------------
# Embedding configuration
# ----------------------------
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "nomic-ai/nomic-embed-text-v1"
)

EMBEDDING_MODEL_ALIAS = os.getenv(
    "EMBEDDING_MODEL_ALIAS",
    "nomic-embed-text"
)

# ----------------------------
# SEC rate limiting
# ----------------------------
REQUESTS_PER_SECOND = float(
    os.getenv("REQUESTS_PER_SECOND", 2.0)
)

# ----------------------------
# Financial heuristics
# ----------------------------
FINANCIAL_KEYWORDS = {
    "revenue", "net sales", "income", "profit", "loss",
    "assets", "liabilities", "equity", "cash flow",
    "operating", "gross margin", "cost of sales",
    "usd", "dollars", "millions"
}

YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")

# ----------------------------
# Language dictionary configuration
# ----------------------------
LANGUAGE_DICT_DIR = CACHE_DIR / "lang_dict"
LANGUAGE_DICT_DIR.mkdir(exist_ok=True)

SUPPORTED_LANGUAGES = ["malay", "tamil", "chinese", "english"]
LANGUAGE_VALIDATION_ENABLED = True
CULTURAL_CONTEXT_ENRICHMENT = True
ALTERNATIVE_SPELLING_TOLERANCE = 0.8

# ----------------------------
# Chunking / processing
# ----------------------------
CHUNK_SIZE = 800
CHUNK_OVERLAP = 160

MAX_IMAGE_SIZE = 1024
MIN_IMAGE_RESOLUTION = 300

SUPPORTED_PDF_TYPES = ["tourism", "technical", "mixed"]
AUTO_DETECT_DOCUMENT_TYPE = True
MIN_TEXT_QUALITY_SCORE = 0.7

# ----------------------------
# Processing outputs
# ----------------------------
PROCESSED_DOCS_DIR = CACHE_DIR / "processed_documents"
EXTRACTED_IMAGES_DIR = CACHE_DIR / "extracted_images"
METADATA_DIR = CACHE_DIR / "metadata"

for d in [PROCESSED_DOCS_DIR, EXTRACTED_IMAGES_DIR, METADATA_DIR]:
    d.mkdir(exist_ok=True)

# ----------------------------
# Logging
# ----------------------------
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_LEVEL = "INFO"
ENABLE_DETAILED_LOGGING = True

# ----------------------------
# Debug prints (optional)
# ----------------------------
print("✅ Config loaded")
print(f"  BASE_DIR: {BASE_DIR}")
print(f"  CHROMA_DIR: {CHROMA_DIR}")
print(f"  OLLAMA_HOST: {OLLAMA_HOST}")
print(f"  SEC_USER_AGENT: {SEC_USER_AGENT}")
