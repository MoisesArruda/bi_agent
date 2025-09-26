from langchain_huggingface import HuggingFaceEmbeddings
from transformers import pipeline
from sentence_transformers import SentenceTransformer
# import torch
import logging
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

class HuggingFaceEmbeddingsClient:
    """Cliente centralizado para modelos Hugging Face."""
    
    def __init__(self):
        """Inicializa o cliente Hugging Face."""
        self._models_cache = {}
        self._device = self._get_device()

    def _get_device(self) -> int:
        """Determina o dispositivo (CPU/GPU) baseado na disponibilidade."""
        if torch.cuda.is_available():
            return 0  # GPU
        return -1  # CPU

    def _load_model(self, model_name: str, model_type: str):
        """Carrega um modelo específico."""
        try:
            if model_type == "embedding":
                return HuggingFaceEmbeddings(model_name=model_name, device=self._device)
            else:
                raise ValueError(f"Tipo de modelo não suportado: {model_type}")

        except Exception as e:
            logger.error(f"Erro ao carregar modelo {model_name}: {e}")
            raise

    def get_embedding_model(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> HuggingFaceEmbeddings:
        """Retorna modelo de embedding para LangChain."""
        return self._load_model(model_name, "embedding")

if __name__ == "__main__":

    embeddings_client = HuggingFaceEmbeddingsClient()

    embedding_model = embeddings_client.get_embedding_model()
    print(embedding_model)