"""
Embedding manager using Sentence Transformers for fast, local embeddings.
Best suited for bulk indexing and high-throughput pipelines.
"""

import logging
from typing import List, Optional
from pathlib import Path

import torch
from sentence_transformers import SentenceTransformer

# Project config
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from config_bak import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TransformerEmbeddingManager:
    """
    Embedding manager using SentenceTransformer models.
    """

    def __init__(
        self,
        model_name: str = "nomic-ai/nomic-embed-text-v1",
        device: Optional[str] = None,
        normalize: bool = True,
        batch_size: int = 32,
    ):
        """
        Initialize transformer embedding manager.

        Args:
            model_name: SentenceTransformer model name
            device: "cuda", "cpu", or None (auto-detect)
            normalize: Whether to L2-normalize embeddings (recommended)
            batch_size: Batch size for encode()
        """

        self.model_name = model_name
        self.normalize = normalize
        self.batch_size = batch_size

        # Auto device selection
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device

        logger.info(
            f"Loading SentenceTransformer model '{model_name}' on device '{device}'"
        )

        self.model = SentenceTransformer(
            model_name,
            device=device,
            cache_folder=str(CACHE_DIR / "sentence_transformers"),
            trust_remote_code=True
        )

        logger.info(
            f"TransformerEmbeddingManager ready "
            f"(dim={self.model.get_sentence_embedding_dimension()})"
        )

    # -------------------------------------------------
    # Single text embedding
    # -------------------------------------------------
    def generate_text_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text string.
        """

        if not text or not text.strip():
            return None

        try:
            embedding = self.model.encode(
                text,
                normalize_embeddings=self.normalize,
                convert_to_numpy=True,
            )
            return embedding.tolist()
        except Exception as e:
            logger.error("Failed to generate embedding", exc_info=True)
            return None

    # -------------------------------------------------
    # Batch text embeddings (FAST)
    # -------------------------------------------------
    def generate_text_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        Generate embeddings for a batch of texts.
        This is MUCH faster than single calls.

        Args:
            texts: List of strings

        Returns:
            List of embedding vectors
        """

        if not texts:
            return []

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                normalize_embeddings=self.normalize,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 32,
            )

            return embeddings.tolist()

        except Exception as e:
            logger.error("Failed to generate batch embeddings", exc_info=True)
            return None

    # -------------------------------------------------
    # Metadata
    # -------------------------------------------------
    @property
    def embedding_dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()
