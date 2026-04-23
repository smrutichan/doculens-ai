from __future__ import annotations
import os,pickle
from typing import Any, Dict, List
import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def highlight_text(text: str, query: str) -> str:
    """Highlight query words in text using yellow highlight."""
    words = query.lower().split()
    highlighted = text

    for word in words:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        highlighted = pattern.sub(
            lambda m: f"<mark>{m.group(0)}</mark>",
            highlighted
        )

    return highlighted


class SearchEngine:
    """Search engine with sentence-transformers + TF-IDF fallback."""

    def __init__(self) -> None:
        self.backend_name = "TF-IDF (fallback)"
        self.documents: List[Dict[str, Any]] = []
        self.document_texts: List[str] = []
        self.document_vectors = None
        self.vectorizer: TfidfVectorizer | None = None
        self.model = None
        self._load_embedding_backend()

    def _load_embedding_backend(self) -> None:
        """Try loading sentence-transformers."""
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(
                "all-MiniLM-L6-v2",
                device="cpu",
                cache_folder="model_cache"
            )
            self.backend_name = "sentence-transformers (all-MiniLM-L6-v2)"
        except Exception:
            self.model = None
            self.backend_name = "TF-IDF (fallback)"

    def index_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Index documents with caching."""
        if not documents:
            raise ValueError("No documents were provided.")

        self.documents = documents
        self.document_texts = [doc["text"] for doc in documents]

        cache_file = "embedding_cache.pkl"

        # ✅ LOAD CACHE IF EXISTS
        if os.path.exists(cache_file):
            with open(cache_file, "rb") as f:
                data = pickle.load(f)
                self.document_vectors = data["vectors"]
                self.vectorizer = data.get("vectorizer", None)  # 🔥 fix
                return

        # 🔥 COMPUTE ONLY IF NOT CACHED
        if self.model is not None:
            self.document_vectors = self.model.encode(
                self.document_texts,
                convert_to_numpy=True,
                show_progress_bar=True,   # helpful first time
                normalize_embeddings=True,
                batch_size=32              # 🔥 speed boost
            )
        else:
            self.vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                max_features=5000,
            )
            self.document_vectors = self.vectorizer.fit_transform(self.document_texts)

        # ✅ SAVE CACHE
        with open(cache_file, "wb") as f:
            pickle.dump({
                            "vectors": self.document_vectors,
                            "vectorizer": self.vectorizer  # 🔥 save it
                        }, f)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search and return results with hybrid ranking (semantic + keyword frequency)."""
        clean_query = query.strip().lower()
        if not clean_query:
            return []

        if not self.documents or self.document_vectors is None:
            raise ValueError("Index not built.")

        query_words = clean_query.split()

        # --- similarity ---
        if self.model is not None:
            query_vector = self.model.encode(
                [clean_query],
                convert_to_numpy=True,
                show_progress_bar=False,
                normalize_embeddings=True,
            )
            similarity_scores = np.dot(self.document_vectors, query_vector[0])
        else:
            query_vector = self.vectorizer.transform([clean_query])
            similarity_scores = cosine_similarity(query_vector, self.document_vectors)[0]

        results: List[Dict[str, Any]] = []

        for doc_index in range(len(self.documents)):
            document = self.documents[doc_index]
            text = document["text"].lower()

            similarity_score = float(similarity_scores[doc_index])

            # 🔥 Count keyword frequency
            keyword_count = sum(text.count(word) for word in query_words)

            # 🔥 Combine both scores
            final_score = similarity_score + (0.1 * keyword_count)

            if final_score <= 0:
                continue

            raw_preview = document["text"][:300].strip()
            preview = highlight_text(raw_preview, clean_query)

            if len(document["text"]) > 300:
                preview += "..."

            results.append(
                {
                    "file_name": document["file_name"],
                    "file_path": document["file_path"],
                    "text_preview": preview,
                    "score": final_score,
                    "chunk_index": document["chunk_index"],
                }
            )

        # 🔥 Sort by final score
        results = sorted(results, key=lambda x: x["score"], reverse=True)

        return results[:top_k]