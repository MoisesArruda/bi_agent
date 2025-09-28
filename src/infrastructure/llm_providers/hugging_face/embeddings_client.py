from langchain_huggingface import HuggingFaceEmbeddings
import logging

logger = logging.getLogger(__name__)

class HuggingFaceEmbeddingsClient:
    """Cliente simplificado para modelos Hugging Face."""
    
    def __init__(self):
        """Inicializa o cliente Hugging Face."""
        pass

    def get_embedding_model(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Retorna modelo de embedding para LangChain."""
        try:
            return HuggingFaceEmbeddings(model_name=model_name)
        except Exception as e:
            logger.error(f"Erro ao carregar modelo {model_name}: {e}")
            raise

if __name__ == "__main__":
    # python -m src.infrastructure.llm_providers.hugging_face.embeddings_client
    
    embeddings_client = HuggingFaceEmbeddingsClient()
    embedding_model = embeddings_client.get_embedding_model()
    print(embedding_model)
