"""
Embeddings module
Contains custom embeddings implementations
"""
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
from typing import List


class LocalEmbeddings(Embeddings):
    """Local embeddings using sentence-transformers"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self._dimension = self.model.get_sentence_embedding_dimension()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        return self.model.encode(texts).tolist()

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        return self.model.encode([text])[0].tolist()

    def __call__(self, text: str) -> List[float]:
        """Make the embeddings callable (required by LangChain)"""
        return self.embed_query(text)

    @property
    def dimension(self) -> int:
        return self._dimension

