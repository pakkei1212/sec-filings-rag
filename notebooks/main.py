import time
from time import perf_counter
from statistics import mean
from typing import List, Dict
from collections import Counter

from tqdm.auto import tqdm

from config_bak import (
    VECTOR_DB_PATH,
    OLLAMA_HOST,
    BATCH_SIZE,
    BASE_ARCHIVE,
    SEC_ITEM_MAP,
    REQUESTS_PER_SECOND,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_MODEL_ALIAS,
)


from src.sec_client import get_submissions, download_filing
from src.chroma_manager import ChromaManager
from src.embedding_manager_transformer import TransformerEmbeddingManager

from src.parser.text_parser import extract_text
from src.parser.table_parser import extract_tables
from src.parser.image_parser import extract_images
from src.chunker import split_sections_with_items, chunk_text


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def get_fiscal_year(filing_date: str) -> int:
    return int(filing_date[:4])


def make_doc_id(cik, year, acc, item, chunk_idx) -> str:
    return f"{cik}_10K_{year}_{acc.replace('-', '')}_{item.replace(' ', '')}_{chunk_idx:03d}"


# -------------------------------------------------
# SEC rate limiter
# -------------------------------------------------
REQUESTS_PER_SECOND = 2.0
_INTERVAL = 1.0 / REQUESTS_PER_SECOND
_last_request = 0.0


def sec_wait():
    global _last_request
    now = time.time()
    elapsed = now - _last_request
    if elapsed < _INTERVAL:
        time.sleep(_INTERVAL - elapsed)
    _last_request = time.time()


# -------------------------------------------------
# Optional debug utility
# -------------------------------------------------
def list_repeated_lines(
    text: str,
    min_repeats: int = 3,
    min_length: int = 15,
    max_length: int = 120,
    top_k: int = 30,
):
    lines = [
        line.strip()
        for line in text.splitlines()
        if min_length <= len(line.strip()) <= max_length
    ]

    counts = Counter(lines)
    repeated = [(l, c) for l, c in counts.items() if c >= min_repeats]
    repeated.sort(key=lambda x: x[1], reverse=True)

    print("\n=== Repeated lines ===")
    for line, cnt in repeated[:top_k]:
        print(f"[{cnt:>3}x] {line}")


# -------------------------------------------------
# Main pipeline
# -------------------------------------------------
def main(cik: str, debug: bool = False):
    # ---- Initialize vector store ----
    chroma = ChromaManager(
        persist_directory=VECTOR_DB_PATH,
        embedding_model=EMBEDDING_MODEL_ALIAS
        collection_name="sec_filings",
        base_url=OLLAMA_HOST,
        verbose=0,
    )

    embedding_manager = TransformerEmbeddingManager(
        model_name=EMBEDDING_MODEL_NAME
        batch_size=BATCH_SIZE,
    )

    chroma.reset_collection()
    chroma.get_collection_stats()

    # ---- Load SEC submissions ----
    data = get_submissions(cik)
    recent = data["filings"]["recent"]

    ten_ks = [
        (form, acc, date, doc)
        for form, acc, date, doc in zip(
            recent["form"],
            recent["accessionNumber"],
            recent["filingDate"],
            recent["primaryDocument"],
        )
        if form == "10-K"
    ]

    all_tables: List[Dict] = []

    # ---- Process filings ----
    for form, acc, date, primary_doc in tqdm(ten_ks, desc="Indexing 10-K filings"):
        print(f"\nProcessing {acc} ({date})")

        base_url = f"{BASE_ARCHIVE}/Archives/edgar/data/{cik}/{acc.replace('-', '')}/"

        sec_wait()
        html = download_filing(cik, acc, primary_doc)

        tables = extract_tables(html)
        images = extract_images(html, base_url)
        text = extract_text(html)

        if debug:
            list_repeated_lines(text)

        sections = split_sections_with_items(text)
        fiscal_year = get_fiscal_year(date)

        # ---- Store tables (future structured index) ----
        for idx, table in enumerate(tables):
            all_tables.append({
                "cik": cik,
                "company": data["name"],
                "filing_type": "10-K",
                "filing_date": date,
                "fiscal_year": fiscal_year,
                "accession": acc,
                "table_index": idx,
                "table": table,
                "source": "SEC EDGAR",
            })

        # ---- Chunk & embed narrative text ----
        batch_texts, batch_meta, batch_ids = [], [], []
        indexed = 0
        chunk_lengths = []

        t0 = perf_counter()

        for item_code, section_text in sections:
            section_title = SEC_ITEM_MAP.get(item_code)
            if not section_title:
                continue

            chunks = chunk_text(
                section_text,
                header=f"{item_code} – {section_title}",
            )

            chunk_lengths.extend(len(c) for c in chunks)

            for idx, chunk in enumerate(chunks):
                batch_texts.append(chunk)
                batch_ids.append(make_doc_id(cik, fiscal_year, acc, item_code, idx))
                batch_meta.append({
                    "cik": cik,
                    "company": data["name"],
                    "filing_type": "10-K",
                    "filing_date": date,
                    "fiscal_year": fiscal_year,
                    "accession": acc,
                    "section": item_code,
                    "section_title": section_title,
                    "chunk_index": idx,
                    "content_type": "narrative",
                    "source": "SEC EDGAR",
                })

                if len(batch_texts) >= BATCH_SIZE:
                    _flush_batch(chroma, embedding_manager, batch_texts, batch_meta, batch_ids)
                    indexed += len(batch_texts)
                    batch_texts.clear()
                    batch_meta.clear()
                    batch_ids.clear()

        if batch_texts:
            _flush_batch(chroma, embedding_manager, batch_texts, batch_meta, batch_ids)
            indexed += len(batch_texts)

        elapsed = perf_counter() - t0

        if chunk_lengths:
            avg_len = round(mean(chunk_lengths), 1)
            print(
                f"Indexed {indexed} chunks | "
                f"{elapsed:.2f}s | "
                f"Avg len {avg_len} | "
                f"Min/Max {min(chunk_lengths)}/{max(chunk_lengths)}"
            )


def _flush_batch(chroma, embedder, texts, metas, ids):
    embeddings = embedder.generate_text_embeddings(texts)
    chroma.add_with_embeddings(
        texts=texts,
        embeddings=embeddings,
        metadatas=metas,
        ids=ids,
    )


# -------------------------------------------------
# Entry point
# -------------------------------------------------
if __name__ == "__main__":
    main(cik="0000320193", debug=True)
