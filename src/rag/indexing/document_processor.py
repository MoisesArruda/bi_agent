from typing import List, Dict, Any, Optional
import logging
from .chunker import DocumentChunker

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Processador de documentos para RAG."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunker = DocumentChunker(chunk_size, chunk_overlap)
    
    def process_pdf(self, pdf_path: str, source_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Processa um PDF completo."""
        try:
            # Carrega o PDF
            documents = self.chunker.load_pdf(pdf_path)
            
            # Cria chunks organizados por seção
            chunks = self.chunker.create_sectioned_chunks(documents)
            
            # Adiciona metadados de origem
            source = source_name or pdf_path.split("/")[-1]
            for chunk in chunks:
                chunk["metadata"]["source"] = source
            
            logger.info(f"PDF processado: {len(chunks)} chunks criados")
            return chunks
            
        except Exception as e:
            logger.error(f"Erro ao processar PDF {pdf_path}: {e}")
            raise
    
    def process_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Processa texto simples."""
        try:
            chunks = self.chunker.create_simple_chunks(text)
            
            # Converte para formato de documento
            documents = []
            for i, chunk in enumerate(chunks):
                documents.append({
                    "page_content": chunk,
                    "metadata": {
                        "chunk_id": i,
                        "chunk_type": "simple",
                        **(metadata or {})
                    }
                })
            
            logger.info(f"Texto processado: {len(documents)} chunks criados")
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao processar texto: {e}")
            raise
    

# Funções de conveniência
def process_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """Processa um  PDF."""
    processor = DocumentProcessor()
    return processor.process_pdf(pdf_path)