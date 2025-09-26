from langgraph.graph import END
from src.app.graph.constants import AgentState

def route_supervisor(state: AgentState) -> AgentState:
    if state['next_step'] == 'search_tables_and_schemas':
        return 'Search_Tables_and_Schemas'
    else:
        return END

def route_with_cache(state: AgentState) -> AgentState:
    # if state["messages"][-1].content == "Resposta não encontrada na cache":
    if state["next_step"] == "Agent_SQL_Validator":
        return "Agent_SQL_Validator"
    else:
        return "Agent_SQL_Writer"


def route_search_tables_and_schemas(state: AgentState) -> AgentState:
    if state["next_step"] == "redis_with_cache":
        # state["database_error"] = 1
        return "Redis_With_Cache"
    else:
        return END


def route_sql_validator(state: AgentState) -> str:
    """
    Determina se deve continuar para BI expert ou repetir validação SQL.
    """
    if (state['result_debug_sql'] == "Pass" or 
        state.get('num_retries_debug_sql', 0) >= state.get('max_num_retries_debug', 3)):
        return 'Agent_BI'
    else:
        return 'Agent_SQL_Writer'


def route_to_bi(state: AgentState) -> AgentState:
    if state['result_debug_sql']=="Pass" or state.get('num_retries_debug_sql', 0) >= state.get('max_num_retries_debug', 3):
        return 'Agent_BI'
    else:
        return 'Agent_SQL_Validator'

def route_to_python_code(state: AgentState) -> AgentState:
    if state['next_step'] == 'agent_python_code_data_visualization_generator_node':
        return 'Agent_Python_Generator'
    else:
            return 'Supervisor_Agent'

def route_python_validator(state: AgentState) -> str:
    """
    Determina se deve terminar o workflow ou repetir validação Python.
    """
    if (state['result_debug_python_code_data_visualization'] == "Pass" or 
        state.get('num_retries_debug_python_code_data_visualization', 0) >= state.get('max_num_retries_debug', 3)):
        return "Supervisor_Agent"
    else:
        return "Agent_Python_Generator"
