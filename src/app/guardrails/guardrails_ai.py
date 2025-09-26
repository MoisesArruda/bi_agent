#
import warnings
import os
import logging

warnings.filterwarnings("ignore", category=UserWarning, module="tqdm.auto")
os.environ["TQDM_DISABLE"] = "1"
os.environ["OTEL_TRACES_SAMPLER"] = "always_off"
os.environ["GUARDRAILS_DISABLE_TELEMETRY"] = "true"

from dotenv import load_dotenv
from guardrails.validators import (
    FailResult,
    PassResult,
    register_validator,
    ValidationResult,
    Validator,
)
from guardrails import Guard
from guardrails.hub import ExcludeSqlPredicates
from typing import Dict, Any, Callable, Optional, List
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from guardrails import Guard
from pydantic import BaseModel, Field, validators
import torch
from src.infrastructure.llm_providers.hugging_face.guardrails_client import HuggingFaceGuardrails

hf_client = HuggingFaceGuardrails()

# Função nativa do Guardrails
def validate_query_commands(text: str) -> bool:
    """Validação de comandos SQL usando Guardrails."""

    try:
        guard = Guard().use(ExcludeSqlPredicates, predicates=["Drop","Insert","Update","Delete"], on_fail="exception")
        response = guard.validate(text)
        return response.validation_passed
    except Exception as e:
        response = FailResult(error_message = f"Comandos de modificação (INSERT, UPDATE, DELETE, DROP) não são permitidos. Tente novamente com uma consulta válida.")
        return response.error_message


# Criando as validações
@register_validator(name="query-unimetal-validator", data_type="string")
class QueryValidator(Validator):
    "Validador que permite apenas tópicos permitidos"

    def __init__(self, on_fail=None):
        super().__init__(on_fail=on_fail)

    def _validate(self, value:Any, metadata:Dict) -> ValidationResult:

        logging.info(f"Validando: {value}")

        # Normaliza o texto para minúsculas
        text_lower = str(value).lower()

        # Keyword permitidas
        allowed_keywords = [
            "consulta",
            "busca", 
            "preço",
            "cotação",
            "resultado",
            "informação",
            "dados",
            "relatório",
            "análise"
        ]


        blocked_keywords = [
            "delete",
            "exclua",
            "apague", 
            "remova",
            "update",
            "atualize",
            "inclua",
            "remove",
            "drop",
            "truncate"
        ]

        # Verifica bloqueios com base exatamanete no que o usuário pediu
        for blocked in blocked_keywords:
            if blocked in text_lower:
                return FailResult(
                    error_message = f"Tópico '{blocked}' não permitido. Por favor, tente novamente com uma consulta válida."
                )
        
        if not any(allowed_words in text_lower  for allowed_words in allowed_keywords):
            return FailResult(
                error_message = "Por favor, faça uma consulta válida."
            )

        return PassResult()



@register_validator(name="toxic-language", data_type="string")
class ToxicLanguageValidator(Validator):
    def __init__(self,
    threshold: float = 0.5,
    model_name: str = "unitary/toxic-bert",
    on_fail = None
    ):
        super().__init__(on_fail=on_fail, threshold=threshold)
        self._threshold = threshold
        self.pipeline = hf_client.get_toxic_classifier(model_name)

    def _validate(self, value: str, metadata: Dict) -> ValidationResult:
        try:
            result = self.pipeline(value)
        # Verifica se o resultado é válido
            if result[0]['label'] == 'toxic' and result[0]['score'] > self._threshold:
                # Para o modelo de sentimentos, 'NEGATIVE' indica conteúdo tóxico
                return FailResult(error_message="toxic message")
            else:
                return PassResult()
        except Exception as e:
            print(f"Aviso: Erro na validação tóxica: {e}")
            return PassResult()


@register_validator(name="semantic-topic-validator", data_type="string")
class SemanticTopicValidator(Validator):
    def __init__(
        self,
        ref_queries = None,
        threshold = 0.7,
        model_name = "all-MiniLM-L6-v2",
        on_fail = None,
    ):
        super().__init__(
            on_fail=on_fail, ref_queries=ref_queries, threshold=threshold
        )
        self._ref_queries = ref_queries
        self._threshold = float(threshold)
        
        # Modelo como atributo da classe
        self._embedding_model = hf_client.get_sentence_transformer(model_name)
        
        if not self._ref_queries:
            raise ValueError("Você precisa fornecer 'ref_queries' para este validador.")

        # Usa o modelo da classe
        self._ref_embeddings = self._embedding_model.encode(
            self._ref_queries, convert_to_tensor=True
        )

    def validate(self, value: Any, metadata: Dict) -> ValidationResult:
        """Validação principal."""

        # 1. Verificação Rápida de Palavras-Chave Bloqueadas (Melhor Prática Híbrida)
        # É bom manter essa verificação rápida para bloquear tentativas óbvias
        blocked_keywords = [
            "delete", "exclua","excluir", "apague", "remova", "update", "atualize",
            "inclua", "remove", "drop", "truncate, insert"
        ]
        text_lower = str(value).lower()
        for blocked in blocked_keywords:
            if blocked in text_lower:
                return FailResult(
                    error_message=f"Ação do tipo '{blocked}' não é permitida.",
                )

        # 2. Verificação Semântica
        logging.info(f"Validando semanticamente: '{value}'")
        logging.info(f"Frases de referência: {self._ref_queries}")
        logging.info(f"Limiar de similaridade: {self._threshold}")

        # Gera o embedding para a consulta do usuário
        query_embedding = self._embedding_model.encode(value, convert_to_tensor=True)

        # Calcula a similaridade de cosseno entre a consulta e todas as frases de referência
        cosine_scores = util.cos_sim(query_embedding, self._ref_embeddings)

        # Pega a maior similaridade encontrada
        max_score = torch.max(cosine_scores).item()
        logging.info(f"Maior score de similaridade: {max_score:.4f}")

        # Verifica se a maior similaridade ultrapassa o limiar
        if max_score < self._threshold:
            return FailResult(
                error_message=(
                    f"Sua pergunta com score de similaridade ({max_score:.2f}) "
                    f"não parece ser sobre os tópicos permitidos. "
                    "Por favor, reformule sua consulta."
                )
            )

        return PassResult()


if __name__ == "__main__":

    # Testando validate_query_comands
    response = validate_query_commands("delete * from employees;")  # Validator passes
    print(response)