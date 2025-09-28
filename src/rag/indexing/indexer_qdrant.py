from typing import List, Dict, Any, Optional
import logging
from .base_indexer import BaseVectorStoreIndexer
from src.db_vector.qdrant.client import QdrantClient

logger = logging.getLogger(__name__)

class QdrantVectorStoreIndexer(BaseVectorStoreIndexer):
    """Indexador usando QdrantClient customizado."""
    
    def __init__(self, embedder: Optional[DocumentEmbedder] = None, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        super().__init__(embedder, model_name)
        self.client = QdrantClient()
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Indexa documentos no Qdrant."""
        try:
            # Usa o DocumentEmbedder para gerar embeddings
            embedded_docs = self._prepare_documents(documents)
            
            # Indexa usando o QdrantClient
            success = self.client.index(embedded_docs)
            
            if success:
                logger.info(f"✅ {len(documents)} documentos indexados no Qdrant usando {self.embedder.model_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao indexar documentos no Qdrant: {e}")
            return False
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Busca documentos similares no Qdrant."""
        try:
            # Gera embedding da consulta
            query_embedding = self.embedder.embed_query(query)
            
            # Busca usando o QdrantClient
            results = self.client.search(query_embedding, k)
            
            logger.debug(f"Busca no Qdrant retornou {len(results)} resultados")
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca no Qdrant: {e}")
            return []
    
    def save_index(self, path: str) -> bool:
        """Salva o índice Qdrant."""
        try:
            success = self.client.save(path)
            if success:
                logger.info(f"Índice Qdrant salvo em: {path}")
            return success
        except Exception as e:
            logger.error(f"Erro ao salvar índice Qdrant: {e}")
            return False
    
    def load_index(self, path: str) -> bool:
        """Carrega o índice Qdrant."""
        try:
            success = self.client.load(path)
            if success:
                logger.info(f"Índice Qdrant carregado de: {path}")
            return success
        except Exception as e:
            logger.error(f"Erro ao carregar índice Qdrant: {e}")
            return False