" Orquestra todo o processo RAG "

from typing import List, Dict, Any
from .retrieval.retriever import DocumentRetriever
from .generation.generator import ResponseGenerator
from .indexing.embedder import DocumentEmbedder
from .indexing.indexer import VectorStoreIndexer  # Nova importação

class RAGPipeline:
    """Pipeline principal do RAG."""
    
    def __init__(self, use_langchain: bool = False):
        if use_langchain:
            # Usar LangChain + FAISS
            self.indexer = VectorStoreIndexer()
            self.retriever = None  # Não precisa do retriever customizado
        else:
            # Usar implementação customizada
            self.retriever = DocumentRetriever()
            self.indexer = None
        
        self.generator = ResponseGenerator()
        self.embedder = DocumentEmbedder()
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Indexa documentos no banco vetorial."""
        if self.indexer:
            # Usar LangChain
            return self.indexer.index_documents(documents)
        else:
            # Usar implementação customizada
            embeddings = self.embedder.embed_documents(documents)
            return self.retriever.index(embeddings, documents)
    
    def query(self, question: str, context: str = None) -> Dict[str, Any]:
        """Executa o pipeline RAG completo."""
        if self.indexer:
            # Usar LangChain
            relevant_docs = self.indexer.search(question, k=5)
        else:
            # Usar implementação customizada
            relevant_docs = self.retriever.retrieve(question)
        
        # Geração
        response = self.generator.generate(question, relevant_docs)
        
        return {
            "answer": response,
            "sources": relevant_docs,
            "metadata": {"pipeline": "rag"}
        }