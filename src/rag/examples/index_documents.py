from src.rag.indexing.document_processor import process_single_pdf
from src.rag.indexing.embedder import embed_documents_simple
from src.db_vector.faiss.client import FaissClient

def index_pdf_documents():
    """Exemplo completo de indexação de documentos."""
    
    # 1. Processar PDF
    print("�� Processando PDF...")
    pdf_path = "data/pdf/Visão de longo prazo Netflix.pdf"
    documents = process_single_pdf(pdf_path)
    print(f"✅ {len(documents)} chunks criados")
    
    # 2. Gerar embeddings
    print("🧠 Gerando embeddings...")
    embedded_docs = embed_documents_simple(documents)
    print(f"✅ {len(embedded_docs)} embeddings gerados")
    
    # 3. Armazenar no banco vetorial
    print("💾 Armazenando no banco vetorial...")
    faiss_client = FaissClient()
    
    # Extrair embeddings e textos
    embeddings = [doc["metadata"]["embedding"] for doc in embedded_docs]
    texts = [doc["page_content"] for doc in embedded_docs]
    metadatas = [doc["metadata"] for doc in embedded_docs]
    
    # Indexar no FAISS
    faiss_client.index_documents(embeddings, texts, metadatas)
    print("✅ Documentos indexados com sucesso!")
    
    return len(embedded_docs)

if __name__ == "__main__":
    total_docs = index_pdf_documents()
    print(f"🎉 Processo concluído! {total_docs} documentos indexados.")