from typing import List, Dict, Any, Optional
import logging
import os
from langchain_community.vectorstores import FAISS
from src.rag.indexing.embedder import DocumentEmbedder

logger = logging.getLogger(__name__)

class FaissVectorStoreIndexer:
    """Indexador usando FAISS com armazenamento local."""
    
    def __init__(self, embedder: Optional[DocumentEmbedder] = None, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Inicializa o indexador com um DocumentEmbedder."""
        self.embedder = embedder or DocumentEmbedder(model_name)
        self.vector_store = None
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Indexa documentos no FAISS."""
        try:
            # Usa o DocumentEmbedder para gerar embeddings
            texts = [doc["page_content"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]
            
            # Criar vetor store usando embeddings já gerados
            self.vector_store = FAISS.from_texts(
                texts=texts,
                embedding=self.embedder.embedding_model,
                metadatas=metadatas,
            )
            
            logger.info(f"✅ {len(documents)} documentos indexados no FAISS usando {self.embedder.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao indexar documentos no FAISS: {e}")
            return False
    
    def save_index(self, path: str) -> bool:
        """Salva o índice FAISS localmente."""
        try:
            if not self.vector_store:
                logger.error("Nenhum índice FAISS para salvar")
                return False
            
            # Garantir que o diretório existe
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Salvar usando o método nativo do FAISS
            self.vector_store.save_local(path)
            logger.info(f"Índice FAISS salvo em: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar índice FAISS: {e}")
            return False
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Busca documentos similares no FAISS."""
        if not self.vector_store:
            logger.error("Nenhum índice FAISS carregado")
            return []
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            
            # Converter para formato padrão
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "text": result.page_content,
                    "metadata": result.metadata,
                })
            
            logger.debug(f"Busca no FAISS retornou {len(formatted_results)} resultados")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Erro na busca no FAISS: {e}")
            return []

    def load_index(self, path: str) -> bool:
        """Carrega o índice FAISS do disco."""
        try:
            if not os.path.exists(path):
                logger.error(f"Índice FAISS não encontrado em: {path}")
                return False
            
            # Carregar usando o método nativo do FAISS
            self.vector_store = FAISS.load_local(path, self.embedder.embedding_model, allow_dangerous_deserialization=True)
            logger.info(f"Índice FAISS carregado de: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar índice FAISS: {e}")
            return False
    
    def get_embedder(self) -> DocumentEmbedder:
        """Retorna a instância do DocumentEmbedder para uso externo."""
        return self.embedder

# Função de conveniência
def index_documents_simple(documents: List[Dict[str, Any]], model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> FaissVectorStoreIndexer:
    """Função simples para indexar documentos."""
    indexer = FaissVectorStoreIndexer(model_name=model_name)
    indexer.index_documents(documents)
    return indexer

if __name__ == "__main__":
    # python -m src.rag.indexing.indexer_faiss

    # 1. Extrair documentos do PDF
    # from .document_processor import process_pdf
    
    # pdf_path = "data/pdf/Visão de longo prazo Netflix.pdf"
    # documents = process_pdf(pdf_path)  # PDF = Documentos de texto
    # print(f" PDF processado: {len(documents)} documentos extraídos")
    
    # # 2. Indexar os documentos
    # indexer = index_documents_simple(documents)
    # print(f"🔍 {len(documents)} documentos indexados")
    
    # # 3. Salvar o índice
    # save_path = "src/db_vector/faiss/faiss_index"
    # success = indexer.save_index(save_path)
    
    # if success:
    #     print(f"✅ Índice salvo em: {save_path}")
    # else:
    #     print("❌ Erro ao salvar o índice")
    
    # print(f"Indexer criado: {indexer}")

    # Busca por similaridade
    indexer = FaissVectorStoreIndexer()
    save_path = "src/db_vector/faiss/faiss_index"

    indexer.load_index(save_path)
    print(f"Índice carregado: {indexer}")

    query = "Qual a visão de longo prazo da Netflix?"
    results = indexer.search(query, k=3)
    print(f"Resultados da busca: {results}")