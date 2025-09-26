from src.rag.pipeline import RAGPipeline
from src.rag.indexing.document_processor import process_single_pdf
from src.rag.indexing.embedder import embed_documents_simple

def setup_rag_system():
    """Configura o sistema RAG completo."""
    
    print("🚀 Configurando sistema RAG...")
    
    # 1. Indexar documentos (fazer apenas uma vez)
    print("\n�� Etapa 1: Indexação")
    pdf_path = "data/pdf/Visão de longo prazo Netflix.pdf"
    documents = process_single_pdf(pdf_path)
    embedded_docs = embed_documents_simple(documents)
    
    # Armazenar no banco vetorial
    from src.db_vector.faiss.client import FaissClient
    faiss_client = FaissClient()
    embeddings = [doc["metadata"]["embedding"] for doc in embedded_docs]
    texts = [doc["page_content"] for doc in embedded_docs]
    metadatas = [doc["metadata"] for doc in embedded_docs]
    faiss_client.index_documents(embeddings, texts, metadatas)
    
    print(f"✅ {len(embedded_docs)} documentos indexados")
    
    # 2. Criar pipeline RAG
    print("\n🔧 Etapa 2: Criando pipeline")
    rag_pipeline = RAGPipeline()
    
    return rag_pipeline

def ask_questions(rag_pipeline):
    """Faz perguntas ao sistema RAG."""
    
    questions = [
        "Qual é a visão de longo prazo da Netflix?",
        "Como a Netflix planeja competir com outras plataformas?",
        "Quais são os principais desafios da Netflix?"
    ]
    
    print("\n❓ Fazendo perguntas ao sistema RAG:")
    
    for question in questions:
        print(f"\n{'='*60}")
        print(f"❓ Pergunta: {question}")
        print(f"{'='*60}")
        
        # Usar o pipeline RAG
        response = rag_pipeline.query(question)
        
        print(f"�� Resposta: {response['answer']}")
        print(f"\n📚 Fontes utilizadas:")
        for i, source in enumerate(response['sources'][:3], 1):
            print(f"  {i}. {source['text'][:100]}...")

if __name__ == "__main__":
    # Configurar sistema
    rag = setup_rag_system()
    
    # Fazer perguntas
    ask_questions(rag)
    
    print("\n🎉 Sistema RAG funcionando!")