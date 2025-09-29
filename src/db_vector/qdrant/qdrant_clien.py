from qdrant_client import QdrantClient,models
from qdrant_client.http.models import PointStruct
from dotenv import load_dotenv
import os

load_dotenv(".env")

COLLECTION = os.getenv("QDRANT_COLLECTION_NAME", "bi_agent_collection")

client = QdrantClient(
    url=os.getenv("QDRANT_URL"), 
    api_key=os.getenv("QDRANT_API_KEY"),
    port = 6333,
    check_compatibility=False
)

def create_collection() -> QdrantClient:
    if client:
        storage = client.get_collections().collections
        storage_names = [collection.name for collection in storage]
    if COLLECTION in storage_names:
        print(f"Collection '{COLLECTION}' já existe.")
        # client.delete_collection(COLLECTION)
    else:
        print(f"Collection '{COLLECTION}' não existe. Criando...")
        client.create_collection(
            collection_name=COLLECTION,
            # Vetor denso (semântico)
            vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
            # Vetor esparso (contextual/BM25)
            sparse_vectors_config={"bm25":models.SparseVectorParams(modifier=models.Modifier.IDF)
            },
        )
        print(f"Collection '{COLLECTION}' criada!")
    collection_info = client.get_collection(COLLECTION)
    print(f"Status: {collection_info.status}")

    return client


