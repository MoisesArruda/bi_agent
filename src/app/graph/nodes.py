import time
import datetime
import pandas as pd
import plotly
import plotly.graph_objects as go
from langgraph.graph import END
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
from src.app.domain.prompts.validator_visualization import system_prompt_agent_python_code_data_visualization_validator
from src.app.graph.utils.utils import build_react_agent, reconstruct_dataframe, serialize_dataframe_to_state, load_data_dictionary, build_memory_context
from langchain_tavily import TavilySearch
from src.databases.redis.client import RedisManager
from src.databases.redis.cache import SQLCache
from redisvl.extensions.cache.llm import SemanticCache
from logs.logs_ import logging_
from src.infrastructure.llm_providers.azure.client import embeddings_model
from src.infrastructure.llm_providers.llm_fabric import create_chain

logger = logging_()

MAX_ERROR_CHARS = 300

def guardrails_node(state: AgentState) -> AgentState:
    """
    Node de guardrails que verifica palavras bloqueadas na pergunta do usuário.
    Bloqueia operações perigosas como DELETE, UPDATE, INSERT, DROP, etc.
    """
    logger.info("\n### Guardrails - Verificando Segurança")
    
    user_question = state.get("question", "").upper()
    
    # Lista de palavras/frases bloqueadas (case-insensitive)
    blocked_keywords = [
        "DELETE", "UPDATE", "INSERT", "DROP", "ALTER", "TRUNCATE","CREATE"
        ]
    
    # Frases específicas bloqueadas
    blocked_phrases = [
        "DROP TABLE", "DROP DATABASE", "DELETE FROM", "UPDATE SET",
        "INSERT INTO", "ALTER TABLE", "TRUNCATE TABLE",
        "CREATE TABLE", "CREATE DATABASE", "GRANT ALL",
        "EXECUTE", "CALL PROCEDURE", "BACKUP DATABASE"
    ]
    
    # Verificar palavras bloqueadas
    blocked_words_found = []
    for keyword in blocked_keywords:
        if keyword in user_question:
            blocked_words_found.append(keyword)
    
    # Verificar frases bloqueadas
    blocked_phrases_found = []
    for phrase in blocked_phrases:
        if phrase in user_question:
            blocked_phrases_found.append(phrase)
    
    # Se encontrou palavras/frases bloqueadas
    if blocked_words_found or blocked_phrases_found:
        logger.warning(f"🚫 Guardrails: Operação bloqueada detectada!")
        logger.warning(f"Palavras bloqueadas encontradas: {blocked_words_found}")
        logger.warning(f"Frases bloqueadas encontradas: {blocked_phrases_found}")
        
        # Mensagem de erro para o usuário
        error_message = f"""
🚫 **Operação Bloqueada por Segurança**

Detectamos que sua pergunta contém operações que podem ser perigosas para o banco de dados:

**Palavras bloqueadas encontradas:** {', '.join(blocked_words_found)}
**Frases bloqueadas encontradas:** {', '.join(blocked_phrases_found)}

**Por favor, reformule sua pergunta para usar apenas operações de consulta (SELECT).**

**Operações permitidas:**
- ✅ SELECT (consultas)
- ✅ JOIN (junções)
- ✅ WHERE (filtros)
- ✅ GROUP BY (agrupamentos)
- ✅ ORDER BY (ordenação)
- ✅ Funções de agregação (COUNT, SUM, AVG, etc.)

**Operações bloqueadas:**
- ❌ DELETE, UPDATE, INSERT
- ❌ DROP, ALTER, TRUNCATE
- ❌ CREATE, GRANT, REVOKE
- ❌ EXEC, EXECUTE, CALL
        """
        
        state["messages"] = [AIMessage(content=error_message)]
        state["next_step"] = END
        return state
    
    # Se passou na verificação, continua o fluxo
    logger.info("✅ Guardrails: Pergunta aprovada - sem operações perigosas")
    state["next_step"] = "search_tables_and_schemas"
    return state

def search_tables_and_schemas(state: AgentState) -> AgentState:
    logger.info("Buscando tabelas, esquemas e colunas no MySql...")

    DB_NAME = "netflix"

    db = AzureSQLManager()

    # schemas_and_table, columns = get_postgres_table_info(DB_NAME)
    for attempt in range(2):

        try:
            schemas_and_table, columns = db.get_table_info(DB_NAME)
        
            if schemas_and_table is not None:
                logger.info((f"✅ Conexão bem-sucedida com o MySql"))
            # print(schemas_and_table)
            # print(columns)
                state["database_schemas"] = schemas_and_table
                state["columns"] = columns
                state["next_step"] = "redis_with_cache"

                return state
        
            else:

                logger.error(f"Erro na tentativa {attempt + 1}")
 

        except Exception as e:
            logger.error(f"Erro na tentativa {attempt + 1}: {e}")
            
            if attempt == 0:
                time.sleep(1)


    logger.error("Falha após 2 tentativas, enviando para o usuário")
    state["messages"] = [AIMessage(content="Erro ao acessar o banco de dados. Por favor, tente novamente mais tarde")]
    state["next_step"] = END
            
    return state

def redis_with_cache(state: AgentState) -> AgentState:
    
    manager = RedisManager()
    redis_client = manager.connect()

    if not redis_client:
        logger.error("❌ Falha na conexão com o Redis. A cache está indisponível.")
        state["messages"] = [AIMessage(content="Resposta não encontrada na cache")]
        state["next_step"] = "agent_sql_writer_node"
        return state

    try:
        cache = SQLCache(redis_client=redis_client)
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cache: {e}")
        state["messages"] = [AIMessage(content="Erro ao acessar cache")]
        state["next_step"] = "agent_sql_writer_node"
        return state
        
    user_question = state.get("question")
    cached_response = cache.get_qa(user_question)

    if cached_response:
        logger.info(f"Resposta cacheada: {cached_response}")
        query_sql = cached_response.get("querye","")
        explanation_query = cached_response.get("explanation_query","")
        python_viz = cached_response.get("python_viz","")

        state["query"] = query_sql
        state["explanation_query"] = explanation_query
        state["python_code_data_visualization"] = python_viz

        state["messages"] = [AIMessage(content=f"Resposta cacheada: {cached_response}")]
        state["next_step"] = "Agent_SQL_Validator"
        return state
    
    logger.info(f"🔍 Cache exato não encontrado. Iniciando busca semântica...")

    try:

        vectorizer = embeddings_model()

        semantic_cache = SemanticCache(
                name="cache-index",
                vectorizer=vectorizer,
                ttl=None,  # Sem expiração
                redis_url=f"redis://{os.getenv('AZURE_REDIS_HOST')}:{os.getenv('AZURE_REDIS_PORT')}",
                distance_threshold=0.2,  # Ajuste conforme necessário (0.2-0.4)
                overwrite=False  # Não recriar o índice
            )

        semantic_result = semantic_cache.check(
            prompt=user_question,
            num_results=1  # Pegar apenas o mais similar
        )

        if semantic_result:
            result = semantic_result[0]
            response_text = result.get('response', '')
            
            logger.info(f"✅ Cache SEMÂNTICO encontrado!")

            # Extrair query SQL e explicação
            if "Query SQL:" in response_text:
                parts = response_text.split("Query SQL:")
                state["explanation_semantic"] = parts[0].replace("Explicação:", "").strip()
                state["query"] = parts[1].strip()
                state["next_step"] = "Agent_SQL_Writer"
                return state
            else:
                logger.info(f"❌ Cache SEMÂNTICO não encontrado!")
                state["next_step"] = "Agent_SQL_Writer"
                return state

    except Exception as e:
        logger.error(f"Falha para acessar o cache: {e}")
        state["messages"] = [AIMessage(content=f"Erro ao buscar resposta na cache: {e}")]
        state["next_step"] = "Agent_SQL_Writer"
        return state

def supervisor_agent_node(state: AgentState) -> AgentState:
    
    logger.info("\n###Agente Supervisor")

    memory_context = build_memory_context(state)
    state["memory_context"] = memory_context

    # ✅ Extrair dados de memória para atualização
    conversation_history = state.get("conversation_history", [])
    last_questions = state.get("last_questions", [])

    if state.get("result_debug_bi") == False:

        try:

            agent_supervisor = create_chain(system_prompt_supervisor_agent, pydantic_object=SupervisorAgentResponse)

            logger.info(f"Pergunta do usuário: {state['question']}")
            agent_supervisor_response = agent_supervisor.invoke({
                "question": state["question"],
                "database_schemas": state.get("database_schemas"),
                "memory_context": last_questions
            })

            state["messages"] = agent_supervisor_response.response
            state["next_step"] = agent_supervisor_response.next_step

            # ✅ ATUALIZAR MEMÓRIA após resposta final
            new_conversation_entry = {
                "question": state["question"],
                "response": agent_supervisor_response.response
            }


            if state["next_step"] == "END":
            
                state["conversation_history"] = conversation_history + [new_conversation_entry]
                state["last_questions"] = last_questions + [state["question"]]

                logger.info(f"Resposta do LLM: {agent_supervisor_response}")

                return state
            else:
                state["question"] = agent_supervisor_response.response
                state["conversation_history"] = conversation_history + [new_conversation_entry]
                state["last_questions"] = last_questions + [agent_supervisor_response]

                return state

        except Exception as e:
            logger.error(f"Erro no roteamento inicial do supervisor: {e}")
            return {
                **state,
                "messages": [{"role": "assistant", "content": "Erro ao processar a pergunta, por favor, tente novamente."}],
                "next_step": END
            }

        # Verifica se o fluxo principal já rodou e deve apenas formatar a resposta final
    else:
        logger.info(">>> Supervisor: Modo de Resposta Final")

        try:
        
        # Cria a cadeia com o prompt de finalização
            chain = create_chain(system_prompt_final_agent, pydantic_object=SupervisorAgentResponse) # Sem pydantic, pois a saída é texto livre
            
            response = chain.invoke({
                "question": state["question"],
                "explanation_query": state.get("explanation_query", "N/A"),
                "visualization_request": state.get("visualization_request", "N/A"),
                "explanation_python_code_data_visualization": state.get("explanation_python_code_data_visualization", "N/A"),
            }).response
            
            logger.info(response) # Atualiza a mensagem final para o usuário

            state["messages"] = [AIMessage(content=response)]
            state["result_debug_bi"] = ""
            state["next_step"] = END

            return state

        except Exception as e:
            logger.error(f"Erro no roteamento final do supervisor: {e}")
            return {
                **state,
                "messages": [{"role": "assistant", "content": "Erro ao processar a pergunta, por favor, tente novamente."}],
                "next_step": END
            }

def agent_tools_node(state: AgentState) -> AgentState:
    logger.info("### Agent Tools")

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

    logger.info(response["messages"][-1].content)
    state["messages"] = [AIMessage(content=response["messages"][-1].content)]

    return state

def agent_sql_writer_node(state: AgentState) -> AgentState:
    """
    Agente que gera a query SQL baseada na pergunta do usuário e nas informações do banco de dados.
    
    Args:
        state: Estado atual do agente.
    Returns:
        Estado atualizado do agente.
    """
    logger.info("### Chamando o Agente SQL Writer")

    try:

        if state.get("query_semantic") and state.get("explanation_semantic"):
            query_semantic = state.get("query_semantic")
            explanation_semantic = state.get("explanation_semantic")
        else:
            query_semantic = ""
            explanation_semantic = ""

        chain = create_chain(system_prompt_agent_sql_writer, pydantic_object=SQLQueryResponse)
        response = chain.invoke({
            "question": state.get("question"),
            "database_schemas": state.get("database_schemas"),
            "columns": state.get("columns"),
            "data_dictionary": load_data_dictionary(),
            "query_semantic": query_semantic,
            "explanation_semantic": explanation_semantic
        })

        logger.info(f"Resposta do LLM: {response.explain}")
        logger.info(f"Query gerada:\n{response.query}")    
        state["query"] = response.query
        state["explanation_query"] = response.explain

        return state

    except Exception as e:
        logger.error(f"Erro no agent_sql_writer_node: {e}")
        return {
            **state,
            "messages": [AIMessage(content=f"Erro ao gerar query SQL: {e}")],
            "next_step": END
        }


def agent_sql_validator_node(state: AgentState) -> AgentState:    

    logger.info("### Começando o Agente SQL Validator")

    try:
        query = state.get("query")
        question = state.get("question")
        result, columns = None, None

        db = AzureSQLManager()
 
        logger.info("🔍 Validando query com EXPLAIN...")
        table_structure = db.get_table_info("netflix")
        if not table_structure: # Um erro na execução do EXPLAIN indica erro de sintaxe
            raise SyntaxError("Falha na validação com EXPLAIN. A query pode estar sintaticamente incorreta.")
        logger.info(f"EXPLAIN resultado: {table_structure}")

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

        logger.info(f"✅ Validação bem-sucedida. DataFrame criado com shape: {state['df_shape']}")
        
        state["result_debug_sql"] = "Pass"
        state["error_msg_debug_sql"] = ""
        if df.empty:
            state["error_msg_debug_sql"] = "Query executada com sucesso, mas não retornou linhas."

        return state

    
    except Exception as e:
        logger.error(f"❌ Erro na validação da query: {e}")
        state["num_retries_debug_sql"] = state.get("num_retries_debug_sql",0) + 1
        state["result_debug_sql"] = "Not Pass"
        state["error_msg_debug_sql"] = str(e)[:MAX_ERROR_CHARS]

        max_retries = state.get("max_num_retries_debug", 3)
        if state["num_retries_debug_sql"] < max_retries:
            logger.info("\n🔄 Tentando corrigir a query...")

            chain = create_chain(system_prompt_agent_sql_validator, pydantic_object=SQLQueryResponse)

            response = chain.invoke({
                "question": question,
                "database_schemas": state.get("database_schemas"),
                "columns": state.get("columns"),
                "query": state.get("query"),
                "error_msg_debug": state["error_msg_debug_sql"],
            })

            state["query"] = response.query
            logger.info(f"\n📝 Query ajustada:\n{state['query']}")
        else:
            logger.info("⚠️ Número máximo de tentativas de correção da query atingido.")
            
        return state



def agent_bi_expert_node(state: AgentState) -> AgentState:

    logger.info("### Começando oAgent BI Expert")

    # df = reconstruct_dataframe(state)
    df_data = state.get("df_data", [])
    
    agent_bi = create_chain(system_prompt_agent_bi_expert, pydantic_object=AgentBiExpertResponse)
    agent_bi_response = agent_bi.invoke({
        "question": state.get("question"),
        "query": state.get("query"),
        "explanation_query": state.get("explanation_query"),
        "df_structure": state.get("df_structure", ""),
        "df_sample": df_data[:5] if df_data else [],
    })

    state["visualization_request"] = agent_bi_response.response
    state["next_step"] = agent_bi_response.next_step
    state["result_debug_bi"] = "Pass"
    logger.info(f"\n### Solicitação de Visualização:\n{agent_bi_response.response}")
    return state

    
def agent_python_code_data_visualization_generator_node(state: AgentState) -> AgentState:

    logger.info(f"\n### Python Data visualization code")

    df_data = state.get("df_data", [])

    chain = create_chain(system_prompt_agent_python_code_data_visualization_generator, pydantic_object=PythonCodeDataVisualizationResponse)
    response = chain.invoke({
        "visualization_request": state["visualization_request"],
        "df_structure": state.get("df_dtypes", {}),
        "df_sample": df_data[:5] if df_data else [],
    })

    logger.info(f"\n### Código de Visualização Gerado:\n{response.explain}")

    state["python_code_data_visualization"] = response.python_code_data_visualization
    state["explanation_python_code_data_visualization"] = response.explain
    
    return state


def agent_python_code_data_visualization_validator_node(state: AgentState) -> AgentState:    

    logger.info("\n### Validador de Código de Visualização")

    try:
        df = reconstruct_dataframe(state)
        
        if df.empty or not state.get("python_code_data_visualization"):
            raise ValueError("DataFrame vazio ou código de visualização ausente. Não é possível validar.")

        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"df não é um DataFrame válido. Tipo: {type(df)}")
        
        exec_globals = {"df": df, "pd": pd, "plotly": plotly, "go": go, "px": px, "plt": plt}
        exec(state.get("python_code_data_visualization"), exec_globals)

        logger.info(f"✅ Validação bem-sucedida.")

        state["python_code_validated"] = True
        state["result_debug_python_code_data_visualization"] = "Pass"

        return state
        

    except Exception as e:
        logger.error(f"❌ Erro na validação do código: {e}")

        state["num_retries_debug_python_code_data_visualization"] = state.get("num_retries_debug_python_code_data_visualization", 0) + 1
        state["result_debug_python_code_data_visualization"] = "Not Pass"
        state["error_msg_debug_python_code_data_visualization"] = str(e)[:MAX_ERROR_CHARS]
        
        max_retries = state.get("max_num_retries_debug", 3)  # Valor padrão 3
        if state["num_retries_debug_python_code_data_visualization"] < max_retries:
            logger.info("\n🔄 Tentando corrigir o código...")
            agent = create_chain(system_prompt_agent_python_code_data_visualization_validator, pydantic_object=PythonCodeDataVisualizationResponse)
            response = agent.invoke({
                "python_code_data_visualization": state.get("python_code_data_visualization"),
                "error_msg_debug": state.get("error_msg_debug_python_code_data_visualization")
            })

            state["python_code_data_visualization"] = response.explain
            logger.info(f"\n Código ajustado:\n {response}")
        else:
            logger.info("⚠️ Número máximo de tentativas de correção do código atingido.")

        return state


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
        "result_debug_bi": False,
        "df_dtypes": {},
        "df_data": [],
        "df_shape": (0, 0),
        "df_columns": [],
        "df_dtypes": {},
        "visualization_request": "",
        "python_code_data_visualization": "",
        "python_code_validated": False,
    }


    state0 = supervisor_agent_node(agent_state_empty)
    print(state0)

    state1 = agent_tools_node(state0)
    print(state1)

    state2 = search_tables_and_schemas(state1)
    print(state2)

    state3 = redis_with_cache(state2)
    print(state3)

    # state4 = agent_sql_writer_node(state3)
    # print(state4)

    # state5 = agent_sql_validator_node(state4)
    # print(state5)

    # state6 = agent_bi_expert_node(state5)
    # print(state6)
    
    # state7 = agent_python_code_data_visualization_generator_node(state6)
    # print(state7)

    # state8 = agent_python_code_data_visualization_validator_node(state7)
    # print(state8)