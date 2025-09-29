from typing import List, Dict, Any
from src.rag.indexing.embedder import DocumentEmbedder
from qdrant_client import QdrantClient
from src.db_vector.vector_store_interface import VectorStoreInterface
import logging

logger = logging.getLogger(__name__)

class QdrantVectorStore(VectorStoreInterface):
    """Wrapper para QdrantClient com interface unificada."""
    
    def __init__(self, embedder: DocumentEmbedder):
        self.embedder = embedder
        self.client = QdrantClient()  # Seu cliente customizado
    
    def index(self, documents: List[Dict[str, Any]]) -> bool:
        """Indexa documentos usando QdrantClient."""
        embedded_docs = self.embedder.embed_documents(documents)
        return self.client.index(embedded_docs)
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Busca usando QdrantClient."""
        query_embedding = self.embedder.embed_query(query)
        return self.client.search(query_embedding, k)

pdf_path = "data/pdf/Visão de longo prazo Netflix.pdf"