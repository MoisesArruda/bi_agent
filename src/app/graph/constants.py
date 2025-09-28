from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

class AgentState(TypedDict):
    state_message: str
    question: str
    Supervisor: bool = False
    messages: Annotated[Sequence[BaseMessage], add_messages]
    database_schemas: str
    next_step: str
    query: str
    columns: list[str]
    max_num_retries_debug: int
    num_retries_debug_sql: int
    result_debug_sql: str
    result_debug_bi: str
    error_msg_debug_sql: str
    df_data: list
    df_shape: tuple
    df_columns: list
    df_dtypes: dict
    explanation_query: str
    visualization_request: str
    python_code_data_visualization: str
    python_code_validated: bool  
    num_retries_debug_python_code_data_visualization: int
    result_debug_python_code_data_visualization: str 
    error_msg_debug_python_code_data_visualization: str

class SupervisorAgentResponse(BaseModel):
    response: str = Field(description="Your response to the user's question in Portuguese-Brazilian")
    next_step: str = Field(description="The next step to be executed or END")

class SQLQueryResponse(BaseModel):
    explain: str = Field(description="The explanation of the query with how columns were used and the logic of the query")
    query: str = Field(description="The SQL query ready to be executed")

class ReactAgentResponse(BaseModel):
    response: str = Field(description="Resposta final clara e direta para o usuário, em Português-Brasileiro.")
    link_sources: str = Field(description="Breve resumo das fontes utilizadas, incluindo links ou deixe vazio caso não tenha usado fontes externas.")

class AgentBiExpertResponse(BaseModel):
    response: str = Field(description="The response to the text, chart or table to be generated in Portuguese-Brazilian")
    next_step: str = Field(description="The next step to be executed or END")

class PythonCodeDataVisualizationResponse(BaseModel):
    explain: str = Field(description="The explanation of the python code for data visualization")
    python_code_data_visualization: str = Field(description="The python code for data visualization")