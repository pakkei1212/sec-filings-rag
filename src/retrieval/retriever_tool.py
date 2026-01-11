from typing import Dict, Any, List, Union, Optional
from pydantic import BaseModel, Field, ConfigDict
from langchain.tools import StructuredTool

from src.retrieval.retriever import retrieve_sec_chunks

Scalar = Union[str, int]

# -----------------------------
# Filter schema (STRICT)
# -----------------------------
class Filters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    and_: Optional[List[Dict[str, Scalar]]] = Field(default=None, alias="and")
    or_: Optional[List[Dict[str, Scalar]]] = Field(default=None, alias="or")

# -----------------------------
# Tool input schema
# -----------------------------
class SecRetrieverInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    filters: Optional[Dict[str, Any]] = None  # raw, normalized later
    top_k: int = Field(default=5, gt=0)

# -----------------------------
# Normalizer (PRE-VALIDATION)
# -----------------------------
def normalize_filters(filters: dict | None) -> dict | None:
    if not filters:
        return None

    and_filters: list = []
    or_filters: list = []

    for f in filters.get("and", []):
        for k, v in f.items():
            if isinstance(v, list):
                for item in v:
                    or_filters.append({k: int(item) if str(item).isdigit() else item})
            else:
                and_filters.append({k: v})

    or_filters.extend(filters.get("or", []))

    return {"and": and_filters, "or": or_filters}

# -----------------------------
# Tool function
# -----------------------------
def sec_retriever_tool(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    Retrieve relevant SEC filing chunks.

    RULES:
    - Filter values must be scalar
    - Ranges must be expanded using OR
    """

    normalized = normalize_filters(filters)
    validated = Filters.model_validate(normalized) if normalized else Filters()

    return retrieve_sec_chunks(
        query=query,
        constraints={
            "filters": {
                "and": validated.and_ or [],
                "or": validated.or_ or [],
            },
            "top_k": top_k,
        }
    )

# -----------------------------
# Structured tool binding
# -----------------------------
sec_retriever_tool = StructuredTool.from_function(
    func=sec_retriever_tool,
    args_schema=SecRetrieverInput,
    name="sec_retriever_tool",
    description="Retrieve SEC filing chunks with strict structured filters",
)
