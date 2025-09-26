from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class VectorStoreIndexer:
    """Indexador usando LangChain + FAISS."""
    
    def __init__(self, embedding_model: str = "openai"):
        """Inicializa o indexador."""
        if embedding_model == "openai":
            self.embeddings = OpenAIEmbeddings()
        else:
            raise ValueError(f"Modelo de embedding não suportado: {embedding_model}")
        
        self.vector_store = None
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Indexa documentos no FAISS."""
        try:
            # Extrair textos e metadados
            texts = [doc["page_content"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]
            
            # Criar vetor store
            self.vector_store = FAISS.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas
            )
            
            logger.info(f"✅ {len(documents)} documentos indexados no FAISS")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao indexar documentos: {e}")
            return False
    
    def save_index(self, path: str) -> bool:
        """Salva o índice em disco."""
        try:
            if self.vector_store:
                self.vector_store.save_local(path)
                logger.info(f"Índice salvo em: {path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao salvar índice: {e}")
            return False
    
    def load_index(self, path: str) -> bool:
        """Carrega o índice do disco."""
        try:
            self.vector_store = FAISS.load_local(path, self.embeddings)
            logger.info(f"Índice carregado de: {path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar índice: {e}")
            return False
    
    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Busca documentos similares."""
        if not self.vector_store:
            logger.error("Nenhum índice carregado")
            return []
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            
            # Converter para formato padrão
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "text": result.page_content,
                    "metadata": result.metadata,
                    "score": 1.0  # FAISS não retorna score por padrão
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []

# Funções de conveniência
def index_documents_simple(documents: List[Dict[str, Any]]) -> VectorStoreIndexer:
    """Função simples para indexar documentos."""
    indexer = VectorStoreIndexer()
    indexer.index_documents(documents)
    return indexer

def search_documents_simple(indexer: VectorStoreIndexer, query: str, k: int = 3) -> List[Dict[str, Any]]:
    """Função simples para buscar documentos."""
    return indexer.search(query, k)