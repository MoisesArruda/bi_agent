import redis
import os
from typing import Optional
from dotenv import load_dotenv
import logging

load_dotenv()

# Configura o sistema de logging
logger = logging.getLogger(__name__)


class RedisManager:
    """
    Gerenciador unificado para Redis - Local e Cloud
    """
    
    def __init__(self):
        self.redis_client = None
        self.environment = self._detect_environment()
        
    def _detect_environment(self) -> str:

        azure_indicators = [
            'AZURE_REDIS_HOST',
            'AZURE_REDIS_PORT',
        ]
        
        # Se qualquer uma das variáveis de ambiente do Azure estiver presente,
        # assumimos que estamos em um ambiente Azure.
        if any(os.getenv(indicator) for indicator in azure_indicators):
            return 'azure'
        
        # Se não houver indicadores do Azure, assume que o ambiente é local.
        return 'local'
    
    def connect(self) -> Optional[redis.Redis]:
        """
        Conecta ao Redis baseado no ambiente detectado
        """
        logging.info(f"🔍 Ambiente detectado: {self.environment}")

        try:
            if self.environment == 'local':
                self.redis_client = self._connect_local()
            elif self.environment == 'azure':
                self.redis_client = self._connect_azure()
            else:
                logging.error("❌ Ambiente não reconhecido, tentando local como fallback...")
                self.redis_client = self._connect_local()

            if self.redis_client and self.redis_client.ping():
                logging.info(f"✅ Conexão bem-sucedida ao Redis no ambiente '{self.environment}'")
                return self.redis_client
            else:
                logging.error("❌ Falha ao conectar ao Redis ou cliente não disponível.")
                return None
                
        except (redis.exceptions.ConnectionError, redis.exceptions.AuthenticationError) as e:
            logging.error(f"❌ Erro de conexão ou autenticação com o Redis: {e}")
            return None
        except Exception as e:
            logging.error(f"❌ Erro inesperado ao conectar ao Redis: {e}")
            return None

    def _connect_local(self) -> redis.Redis:
        """
        Cria e retorna uma instância do cliente Redis para um ambiente local.
        
        Usa variáveis de ambiente para a configuração, com valores padrão
        para facilitar o uso em desenvolvimento.
        """
        host = os.getenv('REDIS_HOST', 'localhost')
        port = int(os.getenv('REDIS_PORT', 6379))
        # db = int(os.getenv('REDIS_DB', 0))

        logging.info(f"🔄 Conectando ao Redis LOCAL em {host}:{port}...")
        
        return redis.Redis(
            host=host,
            port=port,
            # db=db,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
    
    def _connect_azure(self) -> Optional[redis.Redis]:
        """Conecta ao Azure Redis Cache"""
        
        # Prioridade 1: Conexão por URL
        # azure_url = os.getenv('REDIS_AZURE_URL')
        # if azure_url:
        #     logging.info("🔄 Conectando via Azure Redis URL...")
        #     return redis.from_url(
        #         azure_url,
        #         decode_responses=True,
        #         socket_connect_timeout=10,
        #         ssl_cert_reqs=None
        #     )
        
        # # Prioridade 2: Conexão por Connection String
        # connection_string = os.getenv('AZURE_REDIS_CONNECTION_STRING')
        # if connection_string:
        #     logging.info("🔄 Conectando via Azure Redis Connection String...")
        #     return redis.from_url(
        #         f"rediss://{connection_string}",
        #         decode_responses=True,
        #         socket_connect_timeout=10,
        #         ssl_cert_reqs=None
        #     )
            
        # Prioridade 3: Conexão manual
        host = os.getenv('AZURE_REDIS_HOST') or os.getenv('REDIS_HOST')
        # password = os.getenv('AZURE_REDIS_PASSWORD') or os.getenv('REDIS_PASSWORD')
        port = int(os.getenv('AZURE_REDIS_PORT', os.getenv('REDIS_PORT', 10000)))
        
        if host and host:
            logging.info(f"🔄 Conectando ao Azure Redis em {host}:{port}...")
            return redis.Redis(
                host=host,
                port=port,
                decode_responses=True,
                socket_connect_timeout=3,
                health_check_interval=30
            )
        
        logging.error("❌ Nenhuma configuração válida do Azure Redis foi encontrada.")
        return None



if __name__ == "__main__":
    # python -m src.databases.redis.client
    manager = RedisManager()  
    redis_client = manager.connect()

    if redis_client:
        print("Conexão com o Redis estabelecida com sucesso!")
        # Exemplo de uso
        # redis_client.set("chave_teste", "valor_teste")
        # print(redis_client.get("chave_teste"))
    else:
        print("Falha ao conectar com o Redis.")