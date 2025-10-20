import redis
import json
import os
import hashlib
from datetime import datetime
from typing import Optional, Dict, List, Any
import re
from src.databases.redis.client import RedisManager

class SQLCache:
    """
    Cache simples para perguntas e queries SQL
    """

    def __init__(self, redis_client: redis.Redis):
        """
        Inicializa o cache com um cliente Redis já conectado.
        """
        self.redis = redis_client
        try:
            if not self.redis or not self.redis.ping():
                raise Exception("Erro: Cliente Redis não conectado ou inválido!")
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            raise Exception(f"Erro de conexão com Redis: {e}")
        except Exception as e:
            raise Exception(f"Erro ao validar conexão Redis: {e}")
            
    def normalize_question(self, question: str) -> str:
        """Normaliza pergunta para busca"""
        normalized = re.sub(r'[^\w\s]', '', question.lower())
        return ' '.join(normalized.split())

    def hash_question(self, question: str) -> str:
        """Cria hash da pergunta normalizada"""
        normalized = self.normalize_question(question)
        return hashlib.md5(normalized.encode()).hexdigest()[:12]  # 12 chars

    def store_qa(self, question: str, querye: str, **metadata: Any) -> str:
        """
        Armazena pergunta, query e informações adicionais no cache.
        Apenas 'question' e 'querye' são obrigatórias.
        
        Args:
            question (str): A pergunta do utilizador.
            querye (str): A query SQL gerada.
            **metadata (Any): Campos adicionais como fonte, departamento, etc.
        
        Returns:
            str: O hash único da pergunta.
        """
        # Cria um hash único para a pergunta
        question_hash = self.hash_question(question)
        
        # Estrutura principal com as informações obrigatórias e geradas
        entry = {
            "id": question_hash,
            "question": question,
            "querye": querye,
            "data_criacao": datetime.now().strftime("%d/%m/%Y/"),
            "data_atualizacao": datetime.now().strftime("%d/%m/%Y/"),
            "status": "ativo",
            **metadata  # Adiciona os dados extras do **kwargs
        }
        
        # Armazena a entrada como uma string JSON no Redis.
        # Usa SETEX para definir um tempo de expiração (30 dias)
        key = f"sql_cache:{question_hash}"
        self.redis.setex(key, 86400 * 30, json.dumps(entry, ensure_ascii=False))  # 30 dias
        
        print(f"✅ Cache salvo: {question_hash}")
        return question_hash

    def get_qa(self, question: str) -> Optional[Dict]:
        """
        Busca pergunta no cache
        """
        question_hash = self.hash_question(question)
        key = f"sql_cache:{question_hash}"
        
        result = self.redis.get(key)
        if result:
            return json.loads(result)
        return None

    def list_all_cache(self) -> List[Dict]:
        """
        Lista todo o cache de SQL
        """
        keys = self.redis.keys("sql_cache:*")
        results = []
        
        for key in keys:
            data = self.redis.get(key)
            if data:
                results.append(json.loads(data))
        return results

    def delete_cache(self, question: str) -> bool:
        """
        Deleta entrada do cache
        """
        question_hash = self.hash_question(question)
        key = f"sql_cache:{question_hash}"
        return bool(self.redis.delete(key))


# --- Exemplo de Uso ---
# Este é um exemplo de como a sua classe SQLCache deve ser usada.

if __name__ == "__main__":
    try:
        manager = RedisManager()
        redis_client = manager.connect()

        if redis_client:
            sql_cache = SQLCache(redis_client=redis_client)

            # # Exemplo de uso 1: Apenas com os campos obrigatórios
            # print("--- Exemplo 1: Campos obrigatórios ---")
            # question_1 = "Quero todos os registros da tabela"
            # query_1 = "SELECT * FROM TB_COMERCIAL"
            # sql_cache.store_qa(question=question_1, querye=query_1)

            # # Exemplo de uso 2: Com todos os campos adicionais
            # print("\n--- Exemplo 2: Todos os campos ---")
            # data_completa = {
            #     "fonte": "DW.TB_COMERCIAL",
            #     "departamento": "Vendas",
            #     "question": "qual o numero de propostas feitas para o cliente gerdau por filial e municipio",
            #     "querye": "SELECT CONCAT(M0_CODFIL,M0_FILIAL) ...",
            #     "python_viz": "",
            #     "usuario_criacao": "Everton Ribeiro", 
            # }
            # sql_cache.store_qa(**data_completa) # O ** desempacota o dicionário em argumentos de palavra-chave

            # Buscar do cache (usando a pergunta completa)
            resultado_cache = sql_cache.get_qa("Quero todos os registros da tabela")
            if resultado_cache:
                print("\nResultado encontrado no cache:")
                print(json.dumps(resultado_cache, indent=2))
            else:
                print("\nNão foi possível encontrar a pergunta no cache.")

        else:
            print("Não foi possível conectar ao Redis. O cache não será usado.")

    except Exception as e:
        print(f"Ocorreu um erro geral: {e}")