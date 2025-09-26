from src.rag.indexing.embedder import embed_query_simple
from src.db_vector.faiss.client import FaissClient

def retrieve_relevant_documents(query: str, top_k: int = 5):
    """Exemplo de recuperação de documentos relevantes."""
    
    print(f"🔍 Buscando documentos para: '{query}'")
    
    # 1. Gerar embedding da consulta
    print("🧠 Gerando embedding da consulta...")
    query_embedding = embed_query_simple(query)
    print(f"✅ Embedding gerado: {len(query_embedding)} dimensões")
    
    # 2. Buscar no banco vetorial
    print("🔎 Buscando no banco vetorial...")
    faiss_client = FaissClient()
    results = faiss_client.search(query_embedding, top_k)
    print(f"✅ {len(results)} documentos encontrados")
    
    # 3. Mostrar resultados
    print("\n📋 Documentos relevantes:")
    for i, result in enumerate(results, 1):
        print(f"\n--- Documento {i} ---")
        print(f"Conteúdo: {result['text'][:200]}...")
        print(f"Seção: {result['metadata'].get('section', 'N/A')}")
        print(f"Página: {result['metadata'].get('page', 'N/A')}")
        print(f"Score: {result['score']:.4f}")
    
    return results

if __name__ == "__main__":
    # Exemplos de consultas
    queries = [
        "Qual é a visão da Netflix?",
        "Como a Netflix planeja crescer?",
        "Quais são os desafios da Netflix?"
    ]
    
    for query in queries:
        print(f"\n{'='*50}")
        results = retrieve_relevant_documents(query)
        print(f"{'='*50}")