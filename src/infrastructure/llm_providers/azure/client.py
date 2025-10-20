from abc import ABC, abstractmethod
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os
from typing import Optional
import logging
from redisvl.utils.vectorize import AzureOpenAITextVectorizer

load_dotenv()

logger = logging.getLogger(__name__)


class AzureChatHandler:
    """Gerenciador de modelos Azure OpenAI com métodos dedicados para cada modelo."""

    def __init__(self):
        """Inicializa o handler sem depender de um único config dict."""
        pass  # Pode ser usado para inicializações futuras

    def gpt41_model(self, temperature: float = 0.0) -> AzureChatOpenAI:
        return AzureChatOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY_41"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_41"),
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_41"),
            temperature=temperature
        )

    def o3_mini_model(self) -> AzureChatOpenAI:
        return AzureChatOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY_O3"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_O3"),
            model="o3-mini",
            api_version=os.getenv("AZURE_OPENAI_API_VERSION_O3"),
        )

def embeddings_model() -> AzureOpenAITextVectorizer:

    api_key=os.getenv("AZURE_OPENAI_EMBEDDINGS")
    endpoint=os.getenv("AZURE_EMBEDDINGS_ENDPOINT")
    api_version=os.getenv("OPENAI_API_VERSION")

    return AzureOpenAITextVectorizer(
        api_key=api_key,
        endpoint=endpoint,
        api_version=api_version,
    )



if __name__ == "__main__":
    # python -m src.infrastructure.llm_providers.azure.client
    azure_handler = AzureChatHandler()
    print(azure_handler.gpt41_model().invoke("What is the capital of France?").content)
    print(azure_handler.o3_mini_model().invoke("What is the capital of France?").content)