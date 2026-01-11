import json
import requests
from pathlib import Path
from typing import Dict

from config_bak import (
    BASE_DATA,
    BASE_ARCHIVE,
    SUBMISSIONS_DIR,
    IMAGES_DIR,
    SEC_USER_AGENT,
)

# ----------------------------
# SEC request headers
# ----------------------------
SEC_HEADERS = {
    "User-Agent": SEC_USER_AGENT,
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov",
}

# ----------------------------
# Public API
# ----------------------------
def get_submissions(
    cik: str,
    use_remote_fallback: bool = True,
    save_if_downloaded: bool = True,
) -> Dict:
    """
    Load SEC submissions JSON from local cache if available,
    otherwise optionally fetch from SEC and cache locally.
    """
    cik = cik.zfill(10)
    SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)

    local_path = SUBMISSIONS_DIR / f"CIK{cik}.json"

    # 1️⃣ Try local cache
    if local_path.exists():
        with open(local_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # 2️⃣ Fallback to SEC
    if not use_remote_fallback:
        raise FileNotFoundError(f"Local submissions file not found: {local_path}")

    url = f"{BASE_DATA}/submissions/CIK{cik}.json"
    resp = requests.get(url, headers=SEC_HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # 3️⃣ Cache locally
    if save_if_downloaded:
        with open(local_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    return data


def download_filing(
    cik: str,
    accession: str,
    filename: str,
    timeout: int = 30,
) -> str:
    """
    Download a filing document (HTML / TXT) from SEC EDGAR.
    """
    acc = accession.replace("-", "")
    url = f"{BASE_ARCHIVE}/Archives/edgar/data/{int(cik)}/{acc}/{filename}"

    resp = requests.get(url, headers=SEC_HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp.text
