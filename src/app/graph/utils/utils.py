from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.prebuilt import create_react_agent
from typing import Type, List
from langchain_core.tools import BaseTool
from src.infrastructure.llm_providers.groq.client import GroqChatHandler
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from src.app.graph.constants import AgentState
import pandas as pd
import json

load_dotenv()

def build_memory_context(state: AgentState) -> str:
    """Constrói o contexto de memória uma única vez."""
    conversation_history = state.get("conversation_history", [])
    last_questions = state.get("last_questions", [])

    memory_context = ""
    if conversation_history:
        memory_context = "\n\nHistórico da conversa:\n"
        for entry in conversation_history[-5:]:  # Últimas 5 interações
            memory_context += f"Usuário: {entry.get('question', '')}\n"
            # memory_context += f"Assistente: {entry.get('response', '')[:200]}...\n\n"

    if last_questions:
        memory_context += f"\nÚltimas perguntas do usuário: {', '.join(last_questions[-5:])}"

    return memory_context


def build_react_agent(tools: List[BaseTool], system_prompt: str = None, pydantic_object: Type = None):

    groq_client = GroqChatHandler()
    llm = groq_client.get_model("llama-3.3-70b-versatile")

    agent = create_react_agent(
            model=llm,
            tools=tools,
            response_format=pydantic_object,
            prompt=system_prompt
        )   
    return agent

def reconstruct_dataframe(state: AgentState) -> pd.DataFrame:
    """Reconstrói um DataFrame a partir do estado serializado."""
    df_data = state.get("df_data", [])
    df_columns = state.get("df_columns", [])
    if df_data and df_columns:
        return pd.DataFrame(df_data, columns=df_columns)
    return pd.DataFrame()

def serialize_dataframe_to_state(df: pd.DataFrame, state: AgentState):
    """Serializa um DataFrame e o armazena no estado."""
    if df.empty:
        state["df_data"] = []
        state["df_shape"] = (0, 0)
        state["df_columns"] = []
    else:
        state["df_data"] = df.to_dict('records')
        state["df_shape"] = df.shape
        state["df_columns"] = df.columns.tolist()

def load_data_dictionary(file: str = "dataset/dicionario"):
    """Retorna o dicionário de colunas e descrições para a tabela informada."""
    with open(f"data/{file}.json", "r", encoding="utf-8") as f:
        data_dict = json.load(f)
        return data_dict

if __name__ == "__main__":
    # python -m src.app.graph.utils.utils
    print(load_data_dictionary())

    # create_llm_chain = _create_llm_chain(system_prompt="Você é um assistente de dados.", pydantic_object=None)
    # print(create_llm_chain)


