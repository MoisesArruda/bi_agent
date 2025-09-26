from abc import ABC, abstractmethod
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os
from typing import Optional
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class AzureChatOpenAI:
    """Classe para gerenciar interações com modelos Azure OpenAI."""
    
    def __init__(self):
        """Inicializa o provedor Azure OpenAI."""
        self._config = self._load_configuration()
        self._validate_environment()
    
    def _load_configuration(self) -> dict:
        """Carrega e armazena todas as configurações em cache."""
        return {
            # Configurações padrão
            "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "deployment_name": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
            
            # Configurações O3
            "api_key_o3": os.getenv("AZURE_OPENAI_API_KEY_o3"),
            "endpoint_o3": os.getenv("AZURE_OPENAI_ENDPOINT_o3"),
            "api_version_o3": os.getenv("AZURE_OPENAI_API_VERSION_o3", "2024-12-01-preview"),
            
            # Configurações GPT-4.1
            "api_key_41": os.getenv("AZURE_OPENAI_API_KEY_41"),
            "endpoint_41": os.getenv("AZURE_OPENAI_ENDPOINT_41"),
            "deployment_name_41": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_41"),
        }
    
    def _validate_environment(self) -> None:
        """Valida se as variáveis de ambiente necessárias estão configuradas."""
        required_configs = [
            "api_key",
            "endpoint", 
            "deployment_name"
        ]
        
        missing_configs = [config for config in required_configs if not self._config.get(config)]
        if missing_configs:
            logger.warning(f"Configurações ausentes: {missing_configs}")
    
    def _get_azure_client(
        self,
        api_key: str,
        azure_endpoint: str,
        model: str,
        api_version: str = "2024-12-01-preview",
        temperature: float = 0.0,
        max_completion_tokens: Optional[int] = None
    ) -> AzureChatOpenAI:
        """Cria e retorna um cliente Azure OpenAI configurado."""
        try:
            config = {
                "api_key": api_key,
                "azure_endpoint": azure_endpoint,
                "api_version": api_version,
                "model": model,
                "temperature": temperature
            }
            
            if max_completion_tokens:
                config["max_completion_tokens"] = max_completion_tokens
            
            return AzureChatOpenAI(**config)
            
        except Exception as e:
            logger.error(f"Erro ao criar cliente Azure OpenAI: {e}")
            raise
    
    def gpt4o_model(self, temperature: float = 0.0) -> AzureChatOpenAI:
        """Retorna o modelo GPT-4o configurado."""
        return self._get_azure_client(
            api_key=self._config["api_key"],
            azure_endpoint=self._config["endpoint"],
            model=self._config["deployment_name"],
            api_version=self._config["api_version"],
            temperature=temperature
        )
    
    def o3_mini_model(self, temperature: float = 0.0) -> AzureChatOpenAI:
        """Retorna o modelo O3-mini configurado."""
        return self._get_azure_client(
            api_key=self._config["api_key_o3"],
            azure_endpoint=self._config["endpoint_o3"],
            model="o3-mini",
            api_version=self._config["api_version_o3"],
            temperature=temperature
        )
    
    def gpt4_1_model(self, temperature: float = 0.0) -> AzureChatOpenAI:
        """Retorna o modelo GPT-4.1 configurado."""
        return self._get_azure_client(
            api_key=self._config["api_key_41"],
            azure_endpoint=self._config["endpoint_41"],
            model=self._config["deployment_name_41"],
            api_version=self._config["api_version"],
            temperature=temperature
        )
    