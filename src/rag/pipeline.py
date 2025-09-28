from typing import Dict, Any
import os
from src.rag.indexing.document_processor import DocumentProcessor, process_document
from src.rag.indexing.chunker import DocumentChunker
from src.rag.indexing.embedder import DocumentEmbedder
from src.rag.indexing.indexer_faiss import FaissVectorStoreIndexer
# from src.rag.indexing.indexer_qdrant import QdrantVectorStoreIndexer
from src.rag.generator import ResponseGenerator

class RAGPipeline:
    """Pipeline unificado com suporte a múltiplos vector stores."""
    
    def __init__(self, vector_store_type: str = "faiss"):
        self.embedder = DocumentEmbedder()
        self.chunker = DocumentChunker()
        self.processor = DocumentProcessor(self.chunker)
        self.generator = ResponseGenerator()
        self.vector_store_type = vector_store_type
        
        # Factory pattern para indexadores
        self.indexer = self._create_indexer(vector_store_type)
    
    def _create_indexer(self, store_type: str):
        """Factory para criar indexadores."""
        if store_type == "faiss":
            return FaissVectorStoreIndexer(self.embedder)
        # elif store_type == "qdrant":
        #     return QdrantVectorStoreIndexer(self.embedder)
        else:
            raise ValueError(f"Vector store não suportado: {store_type}")
    
    def index_documents(self, source: str) -> bool:
        """Indexa documentos de uma fonte."""
        # Usar a função standalone process_document em vez do método da classe
        documents = process_document(source)
        return self.indexer.index_documents(documents)
    
    def query(self, question: str) -> Dict[str, Any]:
        """Executa consulta RAG completa."""
        relevant_docs = self.indexer.search(question)
        response = self.generator.generate(question, relevant_docs)
        return {
            "answer": response,
            "sources": relevant_docs
        }
    
    def save_index(self, index_name: str) -> bool:
        """Salva o índice atual com nome personalizado."""
        if self.vector_store_type == "faiss":
            # Salva em src/db_vector/faiss/
            path = f"src/db_vector/faiss/{index_name}"
        elif self.vector_store_type == "qdrant":
            # Salva em src/db_vector/qdrant/
            path = f"src/db_vector/qdrant/{index_name}"
        else:
            raise ValueError(f"Tipo de vector store não suportado: {self.vector_store_type}")
        
        return self.indexer.save_index(path)
    
    def load_index(self, index_name: str) -> bool:
        """Carrega um índice salvo pelo nome."""
        if self.vector_store_type == "faiss":
            # Carrega de src/db_vector/faiss/
            path = f"src/db_vector/faiss/{index_name}"
        elif self.vector_store_type == "qdrant":
            # Carrega de src/db_vector/qdrant/
            path = f"src/db_vector/qdrant/{index_name}"
        else:
            raise ValueError(f"Tipo de vector store não suportado: {self.vector_store_type}")
        
        return self.indexer.load_index(path)

if __name__ == "__main__":
    # python -m src.rag.pipeline

    pipeline_faiss = RAGPipeline("faiss")
    # pipeline_qdrant = RAGPipeline("qdrant")

    pdf_path = "data/pdf/Visão de longo prazo Netflix.pdf"
    
    pipeline_faiss.index_documents(pdf_path)
    # pipeline_qdrant.index_documents(pdf_path)

    result = pipeline_faiss.query("Qual é a visão de longo prazo da Netflix?")
    print(result)

    # result_qdrant = pipeline_qdrant.query("Qual é a visão de longo prazo da Netflix?")
    # print(result_qdrant)