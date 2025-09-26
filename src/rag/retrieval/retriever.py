" Recupera documentos relevantes (etapa de recuperação) "

from typing import List, Dict
from src.db_vector.faiss.client import FaissClient
from src.db_vector.qdrant.client import QdrantClient

class DocumentRetriever:
    """Recuperador de documentos usando bancos vetoriais."""
    
    def __init__(self, vector_db: str = "faiss"):
        if vector_db == "faiss":
            self.client = FaissClient()
        elif vector_db == "qdrant":
            self.client = QdrantClient()
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Recupera documentos relevantes."""
        query_embedding = self.client.encode_query(query)
        results = self.client.search(query_embedding, top_k)
        return results