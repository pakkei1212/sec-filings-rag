from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
CACHE_DIR = BASE_DIR / "cache"
VECTOR_STORE_DIR = BASE_DIR / "vector_store"
LOG_DIR = BASE_DIR / "logs"

SUBMISSIONS_DIR = DATA_DIR / "submissions"
IMAGES_DIR = DATA_DIR / "sec_images"

PROCESSED_DOCS_DIR = CACHE_DIR / "processed_documents"
EXTRACTED_IMAGES_DIR = CACHE_DIR / "extracted_images"
METADATA_DIR = CACHE_DIR / "metadata"
LANGUAGE_DICT_DIR = CACHE_DIR / "lang_dict"

ALL_DIRS = [
    DATA_DIR, CACHE_DIR, VECTOR_STORE_DIR, LOG_DIR,
    SUBMISSIONS_DIR, IMAGES_DIR,
    PROCESSED_DOCS_DIR, EXTRACTED_IMAGES_DIR, METADATA_DIR,
    LANGUAGE_DICT_DIR,
]

def ensure_dirs():
    for d in ALL_DIRS:
        d.mkdir(parents=True, exist_ok=True)
