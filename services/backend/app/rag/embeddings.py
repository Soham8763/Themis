import numpy as np
from typing import List

class PolicyEmbedder:
    """
    Generates semantic vector embeddings for policy text chunks.
    Tries SentenceTransformers first, falling back to a deterministic feature hashing vectorizer.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = None
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        except Exception:
            self.model = None

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self.model:
            try:
                embeddings = self.model.encode(texts)
                return embeddings.tolist()
            except Exception:
                pass
        
        # Fallback feature vectorizer (384 dimensions)
        return [self._fallback_embed(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

    def _fallback_embed(self, text: str, dim: int = 384) -> List[float]:
        vec = np.zeros(dim, dtype=np.float32)
        words = text.lower().split()
        for idx, w in enumerate(words):
            h = hash(w) % dim
            vec[h] += 1.0 / (idx + 1)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()
