import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from app.rag.embeddings import PolicyEmbedder
from app.config import settings

class VectorPolicyStore:
    """
    In-memory / Persistent ChromaDB Vector Store for regulatory policies.
    """
    def __init__(self, persist_dir: str = settings.CHROMA_PERSIST_DIR):
        self.persist_dir = persist_dir
        self.embedder = PolicyEmbedder()
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            os.makedirs(self.persist_dir, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_dir)
            self.collection = self.client.get_or_create_collection(name="themis_policies")
        except Exception:
            self.client = None
            self.collection = None

    def add_policies(self, policies: List[Dict[str, Any]]):
        docs = []
        metadatas = []
        ids = []
        embeddings = []

        for p in policies:
            pid = p.get("policy_id", "")
            title = p.get("title", "")
            category = p.get("category", "")
            content = p.get("content", "")
            
            chunk_text = f"Policy ID: {pid}\nCategory: {category}\nTitle: {title}\nContent: {content}"
            doc_obj = {
                "id": pid,
                "text": chunk_text,
                "metadata": {
                    "policy_id": pid,
                    "category": category,
                    "title": title,
                    "version": p.get("version", "1.0")
                },
                "raw_policy": p
            }
            docs.append(doc_obj)
            ids.append(pid)
            metadatas.append(doc_obj["metadata"])

        self.documents = docs

        # Generate embeddings
        raw_texts = [d["text"] for d in docs]
        emb_list = self.embedder.embed_documents(raw_texts)
        self.embeddings = np.array(emb_list, dtype=np.float32)

        if self.collection:
            try:
                self.collection.add(
                    documents=raw_texts,
                    metadatas=metadatas,
                    ids=ids,
                    embeddings=emb_list
                )
            except Exception:
                pass

    def search_policies(self, query: str, category_filter: Optional[str] = None, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.documents:
            return []

        query_vec = np.array(self.embedder.embed_query(query), dtype=np.float32)

        # Compute cosine similarities
        sims = np.dot(self.embeddings, query_vec) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_vec) + 1e-8
        )

        results = []
        for idx in np.argsort(sims)[::-1]:
            doc = self.documents[idx]
            cat = doc["metadata"]["category"]
            if category_filter and cat.lower() != category_filter.lower():
                continue
            
            res = {
                **doc["raw_policy"],
                "relevance_score": float(sims[idx]),
                "matched_text": doc["text"]
            }
            results.append(res)
            if len(results) >= top_k:
                break

        return results

# Global store singleton
policy_vector_store = VectorPolicyStore()
