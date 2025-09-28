import time
import datetime
import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
from src.app.graph.constants import AgentState, SQLQueryResponse, PythonCodeDataVisualizationResponse, SupervisorAgentResponse, AgentBiExpertResponse, ReactAgentResponse
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END
from src.databases.azure_mysql.client import AzureSQLManager
from src.app.domain.prompts.bi_expert import system_prompt_agent_bi_expert
from src.app.domain.prompts.sql_writer import system_prompt_agent_sql_writer
from src.app.domain.prompts.sql_validator import system_prompt_agent_sql_validator
from src.app.domain.prompts.generator_visualization import system_prompt_agent_python_code_data_visualization_generator
from src.app.domain.prompts.supervisor_agent import system_prompt_supervisor_agent
from src.app.domain.prompts.final_agent import system_prompt_final_agent
from src.app.domain.prompts.react_agent import react_prompt
from src.app.graph.utils.utils import _create_llm_chain, build_react_agent, reconstruct_dataframe, serialize_dataframe_to_state, load_data_dictionary
from langchain_tavily import TavilySearch
from src.databases.redis.client import RedisManager



def search_tables_and_schemas(state: AgentState) -> AgentState:
    print("Buscando tabelas, esquemas e colunas no PostgreSQL...")

    DB_NAME = "netflix"

    db = AzureSQLManager()

    # schemas_and_table, columns = get_postgres_table_info(DB_NAME)
    for attempt in range(2):
        schemas_and_table, columns = db.get_table_info(DB_NAME)
    
        if schemas_and_table is not None:
        # print(schemas_and_table)
        # print(columns)
            state["database_schemas"] = schemas_and_table
            state["columns"] = columns
            state["next_step"] = "redis_with_cache"
        
        else:

            print(f"Erro na tentativa {attempt + 1}")
            if attempt == 0:
                time.sleep(1)
            if attempt == 1:
                print("Falha após 2 tentativas, enviando para o usuário")
            state["messages"] = [AIMessage(content="Erro ao acessar o banco de dados. Por favor, tente novamente mais tarde")]
            state["next_step"] = "END"
            
    return state

def redis_with_cache(state: AgentState) -> AgentState:
    
    # Passo 1 e 2: Usa a classe RedisManager para conectar ao Redis
    manager = RedisManager()
    redis_client = manager.connect()

    # Passo 3: Verifica se a conexão foi bem-sucedida
    if not redis_client:
        print("❌ Falha na conexão com o Redis. A cache está indisponível.")

        state["messages"] = [AIMessage(content="Resposta não encontrada na cache")]
        state["next_step"] = "agent_sql_writer_node"
        return state

    return state

def supervisor_agent_node(state: AgentState) -> AgentState:
    
    print("\n### Supervisor Agent")

    # Verifica se o fluxo principal já rodou e deve apenas formatar a resposta final
    if state.get("result_debug_bi") == "Pass":
        print(">>> Supervisor: Modo de Resposta Final")
        
        # Cria a cadeia com o prompt de finalização
        chain = _create_llm_chain(system_prompt_final_agent) # Sem pydantic, pois a saída é texto livre

        df_data = state.get("df_data", [])
        
        response_text = chain.invoke({
            "question": state["question"],
            "explanation_query": state.get("explanation_query", "N/A"),
            "visualization_request": state.get("visualization_request", "N/A"),
            "explanation_python_code_data_visualization": state.get("explanation_python_code_data_visualization", "N/A"),
            # "python_code_data_visualization": state.get("python_code_data_visualization", "N/A"),
            "format_instructions": SupervisorAgentResponse
        }).content
        
        print(response_text) # Atualiza a mensagem final para o usuário

        state["messages"] = [AIMessage(content=response_text)]
        state["next_step"] = END

        return state

    else:
        print(">>> Supervisor: Modo de Roteamento Inicial")

        chain = _create_llm_chain(system_prompt_supervisor_agent, SupervisorAgentResponse)

        response = chain.invoke({
            "question": state["question"],
            "database_schemas": state.get("database_schemas"),
            "format_instructions": SupervisorAgentResponse
        })
        print(response.response)
        print(f"Próximo passo: {response.next_step}")

        state["messages"] = [AIMessage(content=response.response)]
        state["next_step"] = response.next_step

    return state

def agent_tools_node(state: AgentState) -> AgentState:
    print("### Agent Tools")

    today = datetime.datetime.today().strftime("%Y-%m-%d")

    search_tool = TavilySearch(max_results=3, search_depth="basic")

    formatted_prompt = react_prompt.format(today=today, user_question=state["question"])

    react_agent = build_react_agent(
        tools=[search_tool],
        system_prompt=formatted_prompt,
    )

    response = react_agent.invoke({
        "messages": formatted_prompt
    })

    print(response["messages"][-1].content)
    state["messages"] = [AIMessage(content=response["messages"][-1].content)]

    return state

def agent_sql_writer_node(state: AgentState) -> AgentState:
    print("### Agent SQL Writer")


    chain = _create_llm_chain(system_prompt_agent_sql_writer, SQLQueryResponse)
    response = chain.invoke({
        "question": state.get("question"),
        "database_schemas": state.get("database_schemas"),
        "columns": state.get("columns"),
        "data_dictionary": load_data_dictionary(),
        "format_instructions": SQLQueryResponse
    })
    
    state["query"] = response.query
    state["explanation_query"] = response.explain

    print(response)
    print(f"Query gerada:\n{response.query}")
    
    return state


def agent_sql_validator_node(state: AgentState) -> AgentState:    

    print("### Agent SQL validator")
    
    # DB_DIALECT = "sqlserver"

    try:
        query = state.get("query")
        question = state.get("question")
        result, columns = None, None

        # if DB_DIALECT == 'postgress':
        # PRIMEIRO: Validar com EXPLAIN (dry-run)
        db = AzureSQLManager()
        print("🔍 Validando query com EXPLAIN...")
        table_structure = db.get_table_info("netflix")
        # explain_result = query_sql_server(f"EXPLAIN {query}")
        if not table_structure: # Um erro na execução do EXPLAIN indica erro de sintaxe
            raise SyntaxError("Falha na validação com EXPLAIN. A query pode estar sintaticamente incorreta.")
        print(f"EXPLAIN resultado: {table_structure}")

        result = db._querying(query)

        if result is None:
            raise ConnectionError("A execução da query retornou 'None'")

        if columns is None and result:
            num_columns = len(result[0]) if result else 0
            columns = [f"column_{i}" for i in range(num_columns)]
    

        df = pd.DataFrame(result, columns=columns) if result else pd.DataFrame()
        
        # Heurística para nomear coluna de contagem
        if df.shape == (1, 1) and "count" in query.lower():
            df.columns = ['count']
            
        serialize_dataframe_to_state(df, state)

        print(f"✅ Validação bem-sucedida. DataFrame criado com shape: {state['df_shape']}")
        
        state["result_debug_sql"] = "Pass"
        state["error_msg_debug_sql"] = ""
        if df.empty:
            state["error_msg_debug_sql"] = "Query executada com sucesso, mas não retornou linhas."

        return state

    
    except Exception as e:
        print(f"❌ Erro na validação da query: {e}")
        state["num_retries_debug_sql"] = state.get("num_retries_debug_sql",0) + 1
        state["result_debug_sql"] = "Not Pass"
        state["error_msg_debug_sql"] = str(e)[:MAX_ERROR_CHARS]

        max_retries = state.get("max_num_retries_debug", 3)
        if state["num_retries_debug_sql"] < max_retries:
            print("\n🔄 Tentando corrigir a query...")
            chain = _create_llm_chain(system_prompt_agent_sql_validator)
            corrected_query = chain.invoke({
                "query": state.get("query"),
                "question": state.get("question"),
                "database_schemas": state.get("database_schemas"),
                "columns": state.get("columns"),
                "query": state.get("query"),
                "error_msg_debug": state.get("error_msg_debug_sql")
            }).content
            state["query"] = corrected_query
            print(f"\n📝 Query ajustada:\n{state['query']}")
        else:
            print("⚠️ Número máximo de tentativas de correção da query atingido.")
            
    return state



def agent_bi_expert_node(state: AgentState) -> AgentState:

    print("### Agent BI Expert")

    # df = reconstruct_dataframe(state)
    df_data = state.get("df_data", [])
    
    chain = _create_llm_chain(system_prompt_agent_bi_expert, AgentBiExpertResponse)
    response = chain.invoke({
        "question": state.get("question"),
        "query": state.get("query"),
        "explanation_query": state.get("explanation_query"),
        # "df_columns": list(df.columns),
        "df_structure": state.get("df_structure", ""),
        "df_sample": df_data[:5] if df_data else [],
        "format_instructions": AgentBiExpertResponse
    })

    state["visualization_request"] = response.response
    state["next_step"] = response.next_step
    state["result_debug_bi"] = "Pass"
    print(f"\n### Solicitação de Visualização:\n{response}")
    return state

    
def agent_python_code_data_visualization_generator_node(state: AgentState) -> AgentState:

    print(f"\n### Python Data visualization code")

    df_data = state.get("df_data", [])

    chain = _create_llm_chain(system_prompt_agent_python_code_data_visualization_generator, PythonCodeDataVisualizationResponse)
    response = chain.invoke({
        "visualization_request": state["visualization_request"],
        "df_structure": state.get("df_dtypes", {}),
        "df_sample": df_data[:5] if df_data else [],
        "format_instructions": PythonCodeDataVisualizationResponse
    })

    state["python_code_data_visualization"] = response.python_code_data_visualization
    state["explanation_python_code_data_visualization"] = response.explain
    
    # print(f"\n### Código de Visualização Gerado:\n{response.python_code_data_visualization}")
    return state


def agent_python_code_data_visualization_validator_node(state: AgentState) -> AgentState:    

    print("\n### Validador de Código de Visualização")

    try:
        df = reconstruct_dataframe(state)
        
        if df.empty or not state.get("python_code_data_visualization"):
            raise ValueError("DataFrame vazio ou código de visualização ausente. Não é possível validar.")

        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"df não é um DataFrame válido. Tipo: {type(df)}")
        
        exec_globals = {"df": df, "pd": pd, "plotly": plotly, "go": go, "px": px, "plt": plt}
        exec(state.get("python_code_data_visualization"), exec_globals)

        print(f"✅ Validação bem-sucedida.")

        state["python_code_validated"] = True
        state["result_debug_python_code_data_visualization"] = "Pass"

        return state
        

    except Exception as e:
        print(f"❌ Erro na validação do código: {e}")

        error_fields = {
        "num_retries_debug_python_code_data_visualization": state.get("num_retries_debug_python_code_data_visualization", 0) + 1,
        "result_debug_python_code_data_visualization": "Not Pass",
        "error_msg_debug_python_code_data_visualization": str(e)[:MAX_ERROR_CHARS]
        }
        
        max_retries = state.get("max_num_retries_debug", 3)  # Valor padrão 3
        if error_fields["num_retries_debug_python_code_data_visualization"] < max_retries:
            print("\n🔄 Tentando corrigir o código...")
            chain = _create_llm_chain(system_prompt_agent_python_code_data_visualization_validator)
            response = chain.invoke({
                "python_code_data_visualization": state.get("python_code_data_visualization"),
                "error_msg_debug": state.get("error_msg_debug_python_code_data_visualization")
            }).content

            error_fields["python_code_data_visualization"] = response
            print(f"\n�� Código ajustado:\n {response}")
        else:
            print("⚠️ Número máximo de tentativas de correção do código atingido.")

        return {**state, **error_fields}


if __name__ == "__main__":
    # python -m src.app.graph.nodes
    agent_state_empty = {
        "messages": [],
        "next_step": "",
        "question": "Quais são as novidades da Netflix?",
        "database_schemas": "", # Tentativa realizada: Erro no banco de dados
        "columns": "",
        "query": "",
        "explanation_query": "",
        "max_num_retries_debug": 3,
        "num_retries_debug_sql": 0,
        "result_debug_sql": "",
        "error_msg_debug_sql": "",
        "df": pd.DataFrame(),  # Adicionar DataFrame vazio
        "visualization_request": "",
        "python_code_data_visualization": "",
        "python_code_store_variables_dict": {},
        "num_retries_debug_python_code_data_visualization": 0,
        "result_debug_python_code_data_visualization": "",
        "error_msg_debug_python_code_data_visualization": "",
        "result_debug_bi": "",
        "df_dtypes": {},
        "df_data": [],
        "df_shape": (0, 0),
        "df_columns": [],
        "df_dtypes": {},
        "visualization_request": "",
        "python_code_data_visualization": "",
        "python_code_validated": False,
    }


    # state0 = supervisor_agent_node(agent_state_empty)
    # print(state0)

    state1 = agent_tools_node(agent_state_empty)
    # print(state1)

    # state1 = search_tables_and_schemas(state0)
    # print(state1)

    # state2 = agent_sql_writer_node(state1)
    # print(state2)

    # state3 = agent_sql_validator_node(state2)
    # print(state3)

    # state4 = agent_bi_expert_node(state3)
    # print(state4)
    
    # state5 = agent_python_code_data_visualization_generator_node(state4)
    # print(state5)

    # state6 = agent_python_code_data_visualization_validator_node(state5)
    # print(state6)