from transformers import pipeline
from sentence_transformers import SentenceTransformer
import torch
import logging
from typing import Optional, Dict, Any, List
import os

logger = logging.getLogger(__name__)

class HuggingFaceGuardrails:
    """Cliente centralizado para modelos Hugging Face com responsabilidades separadas."""
    
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
            if model_type == "text_classification":
                return pipeline("text-classification", model=model_name, device=self._device)
            elif model_type == "sentence_transformer":
                return SentenceTransformer(model_name)
            else:
                raise ValueError(f"Tipo de modelo não suportado: {model_type}")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo {model_name}: {e}")
            raise

    def get_toxic_classifier(self, model_name: str = "unitary/toxic-bert") -> Any:
        """Retorna pipeline de classificação de linguagem tóxica."""
        return self._load_model(model_name, "text_classification")

    def get_sentence_transformer(self, model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
        """Retorna modelo SentenceTransformer para embeddings semânticos."""
        return self._get_model(model_name, "sentence_transformer")
    
    def get_sentiment_classifier(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest") -> Any:
        """Retorna pipeline de classificação de sentimento."""
        return self._load_model(model_name, "text_classification")

if __name__ == "__main__":
    guardrails_client = HuggingFaceGuardrails()
    toxic_classifier = guardrails_client.get_toxic_classifier()
    sentiment_classifier = guardrails_client.get_sentiment_classifier()
    print(toxic_classifier)
    print(sentiment_classifier)