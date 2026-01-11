from typing import Dict, Any, Optional
from src.storage.chroma_manager import ChromaManager
from configs.models import EMBEDDING_MODEL_ALIAS
from configs.vector_db import VECTOR_DB_PATH
from src.utils.logger import setup_logger
from configs.paths import LOG_DIR

logger = setup_logger(
    log_dir=LOG_DIR,
    debug=True,
)

def build_chroma_where(filters: dict) -> dict | None:
    and_conditions = filters.get("and", [])
    or_conditions = filters.get("or", [])

    clauses = []

    # AND conditions
    if len(and_conditions) == 1:
        clauses.append(and_conditions[0])
    elif len(and_conditions) > 1:
        clauses.append({"$and": and_conditions})

    # OR conditions
    if len(or_conditions) == 1:
        clauses.append(or_conditions[0])
    elif len(or_conditions) > 1:
        clauses.append({"$or": or_conditions})

    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]

    return {"$and": clauses}

def retrieve_sec_chunks(query: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieve SEC filing chunks using structured constraints.

    Expected constraints schema:
    {
      "query": str,                         # REQUIRED
      "filters": {
        "and": [ {field: value}, ... ],
        "or":  [ {field: value}, ... ]
      },
      "top_k": int
    }
    """

    # -----------------------------
    # 1. Required query
    # -----------------------------
    if not query:
        return {
            "error": "Missing required field: query",
            "constraints": constraints,
        }

    # -----------------------------
    # 2. Filters
    # -----------------------------
    filters = constraints.get("filters", {})
    and_filters = filters.get("and", [])
    or_filters = filters.get("or", [])

    where = build_chroma_where(filters)
    # -----------------------------
    # 3. top_k
    # -----------------------------
    top_k = constraints.get("top_k", 5)
    if not isinstance(top_k, int) or top_k <= 0:
        top_k = 5

    logger.debug(
        "retrieve_sec_chunks | %s",
        {
            "query": query,
            "top_k": top_k,
            "where": where,
        },
    )

    # -----------------------------
    # 4. Execute Chroma query
    # -----------------------------
    chroma = ChromaManager(
        persist_directory=VECTOR_DB_PATH,
        embedding_model=EMBEDDING_MODEL_ALIAS,
        collection_name="sec_filings",
    )

    try:
        return chroma.query(
            query_text=query,
            n_results=top_k,
            where=where,
        )

    except Exception as e:
        logger.exception("Chroma query failed")
        return {
            "error": "Chroma query failed",
            "exception": str(e),
            "query": query,
            "where": where,
        }