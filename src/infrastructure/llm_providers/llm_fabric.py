import os
import logging
from functools import lru_cache
from typing import Optional, Type

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import PydanticOutputParser
from src.infrastructure.llm_providers.azure.client import AzureChatHandler
from src.infrastructure.llm_providers.groq.client import GroqChatHandler

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_llm(provider: str = "azure", model: Optional[str] = None, temperature: float = 0.0):
    """
    Retorna um LLM configurado.
    """
    try:
        if provider == "azure":
            azure_handler = AzureChatHandler()
            
            if model == "azure_41_model":
                return azure_handler.gpt41_model(temperature=temperature)
            elif model == "azure_o3_mini_model":
                return azure_handler.o3_mini_model()
            else:
                # Modelo padrão do Azure
                return azure_handler.gpt41_model(temperature=temperature)
                
        elif provider == "groq":
            groq_handler = GroqChatHandler()
            
            if model == "groq_gpt_4o_model":
                return groq_handler.get_model(model_name="openai/gpt-4o", temperature=temperature)
            elif model == "groq_gpt_4o_mini_model":
                return groq_handler.get_model(model_name="openai/gpt-4o-mini", temperature=temperature)
            elif model == "groq_gpt_oss_model":
                return groq_handler.get_model(model_name="openai/gpt-oss-120b", temperature=temperature)
            else:
                # Modelo padrão do Groq
                return groq_handler.get_model(model_name="openai/gpt-4o-mini", temperature=temperature)
        else:
            raise ValueError(f"Provedor desconhecido: {provider}")
            
    except Exception as e:
        logging.warning(f"Erro ao carregar modelo '{model}' com provedor '{provider}': {e}")
        logging.info("Tentando fallback para Groq...")
        
        try:
            groq_handler = GroqChatHandler()
            return groq_handler.get_model(model_name="openai/gpt-4o-mini", temperature=temperature)
        except Exception as fallback_error:
            logging.error(f"Falha no fallback para Groq: {fallback_error}")
            raise RuntimeError("Nenhum modelo pôde ser carregado.")


def create_chain(
    system_prompt: str,
    pydantic_object: Optional[Type] = None,
    provider: str = "azure",
    model: Optional[str] = None,
) -> Runnable:
    """
    Cria uma cadeia LCEL (Prompt -> LLM), opcionalmente com structured output.
    """
    llm = get_llm(provider=provider, model=model, temperature=0.0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt)
    ])

    if pydantic_object:
        try:
            if provider == "azure":
                structured = llm.with_structured_output(pydantic_object)
                return prompt | structured
            else:
                structured = PydanticOutputParser(pydantic_object=pydantic_object)
                prompt_template = prompt.partial(format_instructions=structured.get_format_instructions())
                return prompt_template | llm | structured
        except Exception as e:
            logger.warning(f"Structured output indisponível, fallback para texto. Motivo: {e}")
            return prompt | llm
    
    return prompt | llm


if __name__ == "__main__":
    # python -m src.infrastructure.llm_providers.llm_fabric
    print("=== Testando Azure ===")
    try:
        llm = get_llm(provider="azure", model="azure_41_model", temperature=0.0)
        response = llm.invoke("What is the capital of France?")
        print(f"Azure Response: {response.content}")
    except Exception as e:
        print(f"Erro no Azure: {e}")
    
    print("\n=== Testando Groq ===")
    try:
        llm = get_llm(provider="groq", model="groq_gpt_4o_mini_model", temperature=0.0)
        response = llm.invoke("What is the capital of France?")
        print(f"Groq Response: {response.content}")
    except Exception as e:
        print(f"Erro no Groq: {e}")
    
    print("\n=== Testando Chain ===")
    try:
        chain = create_chain(
            system_prompt="You are a helpful assistant.", 
            provider="azure", 
            model="azure_41_model"
        )
        response = chain.invoke({"messages": [{"role": "user", "content": "What is the capital of France?"}]})
        print(f"Chain Response: {response.content}")
    except Exception as e:
        print(f"Erro na Chain: {e}")