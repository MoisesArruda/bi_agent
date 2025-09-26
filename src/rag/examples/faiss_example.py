from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from src.rag.indexing.document_processor import process_single_pdf
import os

def langchain_faiss_example():
    """Exemplo usando LangChain + FAISS diretamente."""
    
    print("🚀 Exemplo LangChain + FAISS")
    
    # 1. Processar PDF
    print("\n�� Processando PDF...")
    pdf_path = "data/pdf/Visão de longo prazo Netflix.pdf"
    final_docs = process_single_pdf(pdf_path)
    print(f"✅ {len(final_docs)} documentos processados")
    
    # 2. Configurar embeddings
    print("\n🧠 Configurando embeddings...")
    embeddings = OpenAIEmbeddings()
    
    # 3. Preparar dados
    texts = [doc["page_content"] for doc in final_docs]
    metadatas = [doc["metadata"] for doc in final_docs]
    
    # 4. Criar vetor store
    print("\n💾 Criando vetor store FAISS...")
    db = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
    print("✅ Vetor store criado")
    
    # 5. Exemplo de busca
    print("\n🔍 Exemplo de busca:")
    query = "Quais são os concorrentes mais fortes da Netflix?"
    results = db.similarity_search(query, k=3)
    
    print(f"Pergunta: {query}")
    print(f"Resultados encontrados: {len(results)}")
    
    for i, r in enumerate(results, 1):
        print(f"\n--- Resultado {i} ---")
        print(f"SEÇÃO: {r.metadata.get('section', 'N/A')}")
        print(f"PÁGINA: {r.metadata.get('page', 'N/A')}")
        print(f"CONTEÚDO: {r.page_content[:200]}...")
        print("---")
    
    # 6. Salvar índice
    print("\n�� Salvando índice...")
    db.save_local("data/vector_store/faiss_index")
    print("✅ Índice salvo")
    
    return db

def load_and_search_example():
    """Exemplo de carregar índice e fazer busca."""
    
    print("\n🔄 Carregando índice e fazendo busca...")
    
    # Carregar índice
    embeddings = OpenAIEmbeddings()
    db = FAISS.load_local("data/vector_store/faiss_index", embeddings)
    
    # Fazer busca
    queries = [
        "Como a Netflix planeja crescer?",
        "Quais são os desafios da Netflix?",
        "Qual é a estratégia da Netflix?"
    ]
    
    for query in queries:
        print(f"\n❓ Pergunta: {query}")
        results = db.similarity_search(query, k=2)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.page_content[:100]}...")

if __name__ == "__main__":
    # Executar exemplo
    vector_store = langchain_faiss_example()
    
    # Exemplo de carregamento
    load_and_search_example()
    
    print("\n🎉 Exemplo concluído!")