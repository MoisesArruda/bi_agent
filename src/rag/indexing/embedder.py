" Gera embeddings dos documentos (etapa de indexação) "
from typing import List, Dict, Any
import logging
from src.infrastructure.llm_providers.hugging_face.embeddings_client import HuggingFaceEmbeddingsClient

logger = logging.getLogger(__name__)

class DocumentEmbedder:
    """Gerador de embeddings para documentos."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.embeddings_client = HuggingFaceEmbeddingsClient()
        self.embedding_model = self.embeddings_client.get_embedding_model(model_name)
        self.model_name = model_name
    
    def embed_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Gera embeddings para uma lista de documentos."""
        try:
            embedded_docs = []
            
            for doc in documents:
                # Gera embedding para o conteúdo
                embedding = self.embedding_model.embed_query(doc["page_content"])
                
                # Adiciona embedding aos metadados
                doc_with_embedding = {
                    "page_content": doc["page_content"],
                    "metadata": {
                        **doc["metadata"],
                        "embedding": embedding,
                        "embedding_model": self.model_name
                    }
                }
                embedded_docs.append(doc_with_embedding)
            
            logger.info(f"Embeddings gerados para {len(embedded_docs)} documentos")
            return embedded_docs
            
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings: {e}")
            raise
    
    def embed_query(self, query: str) -> List[float]:
        """Gera embedding para uma consulta."""
        try:
            embedding = self.embedding_model.embed_query(query)
            logger.debug(f"Embedding gerado para consulta: {len(embedding)} dimensões")
            return embedding
        except Exception as e:
            logger.error(f"Erro ao gerar embedding para consulta: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Retorna a dimensão dos embeddings."""
        # Embedding de teste para descobrir a dimensão
        test_embedding = self.embed_query("test")
        return len(test_embedding)

# Funções de conveniência
def embed_documents_simple(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Função simples para gerar embeddings."""
    embedder = DocumentEmbedder()
    return embedder.embed_documents(documents)

def embed_query_simple(query: str) -> List[float]:
    """Função simples para gerar embedding de consulta."""
    embedder = DocumentEmbedder()
    return embedder.embed_query(query)