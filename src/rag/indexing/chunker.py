from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DocumentChunker:
    """Classe para dividir documentos em chunks."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " "]
        )
    
    def load_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Carrega e extrai texto de um PDF."""
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            logger.info(f"PDF carregado: {len(documents)} páginas")
            return documents
        except Exception as e:
            logger.error(f"Erro ao carregar PDF {pdf_path}: {e}")
            raise
    
    def create_simple_chunks(self, text: str) -> List[str]:
        """Cria chunks simples de texto."""
        return self.splitter.split_text(text)
    
    def create_sectioned_chunks(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Cria chunks organizados por seções."""
        sectioned_docs = self._extract_sections(documents)
        return self._chunk_sections(sectioned_docs)
    
    def _extract_sections(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extrai seções dos documentos."""
        sectioned_docs = []
        current_section = "Introdução"
        
        for doc in documents:
            lines = doc.page_content.splitlines()
            buffer = []
            
            for line in lines:
                if self._is_section_title(line):
                    if buffer:
                        sectioned_docs.append({
                            "content": "\n".join(buffer).strip(),
                            "page": doc.metadata.get("page", None),
                            "section": current_section
                        })
                        buffer = []
                    current_section = line.strip()
                else:
                    buffer.append(line)
            
            if buffer:
                sectioned_docs.append({
                    "content": "\n".join(buffer).strip(),
                    "page": doc.metadata.get("page", None),
                    "section": current_section
                })
        
        return sectioned_docs
    
    def _chunk_sections(self, sectioned_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Divide seções em chunks menores."""
        final_docs = []
        
        for section in sectioned_docs:
            chunks = self.splitter.split_text(section["content"])
            
            for chunk in chunks:
                final_docs.append({
                    "page_content": chunk,
                    "metadata": {
                        "page": section["page"],
                        "section": section["section"],
                        "source": "document.pdf",
                        "chunk_type": "sectioned"
                    }
                })
        
        return final_docs
    
    def _is_section_title(self, line: str) -> bool:
        """Detecta se uma linha é um título de seção."""
        line = line.strip()
        if not line:
            return False
        return (
            len(line) < 80
            and line[0].isupper()
            and not line.endswith(".")
        )


def load_and_chunk_pdf(pdf_path: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict[str, Any]]:
    """Função simples para carregar PDF e criar chunks."""
    chunker = DocumentChunker(chunk_size, chunk_overlap)
    documents = chunker.load_pdf(pdf_path)
    return chunker.create_sectioned_chunks(documents)

def create_text_chunks(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """Função simples para criar chunks de texto."""
    chunker = DocumentChunker(chunk_size, chunk_overlap)
    return chunker.create_simple_chunks(text)