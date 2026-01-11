"""
Embedding manager using Sentence Transformers for fast, local embeddings.
Supports text embeddings and optional image → caption → embedding.
"""

import logging
from typing import List, Optional
from pathlib import Path
import base64
import requests

import torch
from sentence_transformers import SentenceTransformer

# Project config
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from configs.paths import CACHE_DIR

class TransformerEmbeddingManager:
    """
    Embedding manager using SentenceTransformer models.
    Designed for SEC-scale RAG pipelines.
    """

    def __init__(
        self,
        embedding_model: str = "nomic-ai/nomic-embed-text-v1",
        vision_model: Optional[str] = "qwen2.5vl:3b",
        base_url: Optional[str] = "http://localhost:11434",
        device: Optional[str] = None,
        normalize: bool = True,
        batch_size: int = 32,
        max_chars: int = 8000,
        request_timeout: int = 30,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize transformer embedding manager.

        Args:
            embedding_model: SentenceTransformer model name
            vision_model: Optional Ollama vision model for image descriptions
            base_url: Base URL for Ollama API
            device: "cuda", "cpu", or None (auto-detect)
            normalize: Whether to L2-normalize embeddings (recommended)
            batch_size: Batch size for encode()
            max_chars: Max characters per text input
            request_timeout: Timeout for API requests
        """

        self.embedding_model = embedding_model
        self.vision_model = vision_model
        self.base_url = base_url
        self.normalize = normalize
        self.batch_size = batch_size
        self.max_chars = max_chars
        self.request_timeout = request_timeout
        self.logger = logger or logging.getLogger(__name__)

        # Auto device selection
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device

        self.logger.info(
            "Loading SentenceTransformer '%s' on %s (normalize=%s, batch=%d)",
            embedding_model, device, normalize, batch_size
        )

        self.model = SentenceTransformer(
            embedding_model,
            device=device,
            cache_folder=str(CACHE_DIR / "sentence_transformers"),
            trust_remote_code=True
        )
        
        self.logger.info(
            f"TransformerEmbeddingManager ready "
            f"(dim={self.model.get_sentence_embedding_dimension()})"
        )

    # -------------------------------------------------
    # Internal helpers
    # -------------------------------------------------
    def _truncate(self, text: str) -> str:
        if len(text) > self.max_chars:
            self.logger.debug(
                "Truncating text from %d → %d chars",
                len(text), self.max_chars
            )
            return text[: self.max_chars]
        return text

    # -------------------------------------------------
    # Text embeddings
    # -------------------------------------------------
    def generate_text_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.
        Always returns a list (empty list on failure).
        """
        if not text or not text.strip():
            return []

        try:
            text = self._truncate(text)

            embedding = self.model.encode(
                text,
                normalize_embeddings=self.normalize,
                convert_to_numpy=True,
            )
            return embedding.tolist()

        except Exception:
            self.logger.exception("Failed to generate text embedding")
            return []

    # -------------------------------------------------
    # Batch text embeddings (FAST)
    # -------------------------------------------------
    def generate_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        Always returns a list (possibly empty).
        """
        if not texts:
            return []

        try:
            texts = [self._truncate(t) for t in texts]

            embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                normalize_embeddings=self.normalize,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 32,
            )

            return embeddings.tolist()

        except Exception:
            self.logger.exception("Failed to generate batch embeddings")
            return []

    def generate_image_description(self, image_path: str) -> Optional[str]:
            """
            Generate description for image using vision model
        
            Args:
            image_path: Path to image file
            
            Returns:
            Text description or None if failed
            """

            if not self.vision_model or not self.base_url:
                self.logger.debug("Vision model not configured; skipping image description")
                return ""
    
            try:
                from configs.prompts import SEC_IMAGE_PROMPT

                # Read and encode image
                with open(image_path, "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode("utf-8")
            
                # Prepare request with image
                request_data = {
                    "model": self.vision_model,
                    "prompt": SEC_IMAGE_PROMPT,
                    "images": [image_data],
                    "stream": False,
                }
            
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=request_data,
                    timeout=self.request_timeout,
                )
            
                if response.status_code != 200:
                    self.logger.error(
                        "Vision model error %s: %s",
                        response.status_code, response.text
                    )
                    return ""

                description = response.json().get("response", "").strip()

                if description == "NON_INFORMATIVE_IMAGE":
                    self.logger.debug("Skipping non-informative image (logo/decorative)")
                    return ""

                if not description:
                    return []   # skip embedding

                if description:
                    self.logger.debug(
                        "Generated image description (%d chars)",
                        len(description)
                    )
                    return description

                self.logger.warning("Empty image description returned")
                return ""

            except Exception:
                self.logger.exception("Failed to generate image description")
                return ""
    
    def generate_embedding_for_image(self, image_path: str) -> List[float]:
        """
        Generate embedding for an image by first creating a description, then embedding that
        
        Args:
            image_path: Path to image file
            
        Returns:
            Embedding vector or None if failed
        """
        description = self.generate_image_description(image_path)
        if not description:
            return []

        return self.generate_text_embedding(description)
    
    # -------------------------------------------------
    # Metadata
    # -------------------------------------------------
    @property
    def embedding_dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()
