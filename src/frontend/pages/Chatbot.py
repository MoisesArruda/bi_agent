import streamlit as st
import os, sys
import uuid
import plotly.io as pio
import pandas as pd
import uuid
from typing import Dict, Any
import csv
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import plotly
from logs.logs_ import logging_
from datetime import datetime
import time

logger = logging_()

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(project_root)

from src.frontend.page_config import remove_sidebar_navigation, configure_page, configure_sidebar_with_button
from src.app.graph.graph import create_workflow
from src.frontend.utils.utils import save_messages

image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "img", 'ArrudaConsulting.jpeg')
dataset_path = os.path.join(project_root, "data", "dataset", "netflix_movies_and_tv_shows.csv")


def initialize_session_state():
    """
    Inicialização mínima necessária
    """

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Olá! Sou um assistente para análise de dados. Como posso te ajudar hoje?"}
        ]

    # ✅ Thread ID único POR SESSÃO (persiste entre perguntas)
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = f"user_{uuid.uuid4()}"
    
    # ✅ Contador de interações (evita cache)
    if "interaction_count" not in st.session_state:
        st.session_state.interaction_count = 0

def execute_workflow(prompt: str) -> Dict[str, Any]:
    """Executa o workflow e retorna o estado final"""

    # Usar thread_id do session_state ou criar um único
    st.session_state.interaction_count += 1
    graph = create_workflow()
    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id,
            "interaction_id": st.session_state.interaction_count,
            "timestamp": datetime.now().isoformat()
        }
    }

    initial_state = {
        "question": prompt,
        # ✅ Campos de memória (persistem entre perguntas)
        "conversation_history": st.session_state.get("conversation_history", []),
        "last_questions": st.session_state.get("last_questions", []),
        "python_code_data_visualization": None,
        "python_code_validated": False,
        "df_data": [],
        "df_columns": [],
        "df_shape": (0, 0),
        "df_dtypes": {},
        "visualization_request": None,
        "visualization_elements": [],
        "query": None,
        "explanation_query": None,
        "result_debug_bi": False,
        "result_debug_sql": None,
        "result_debug_python_code_data_visualization": None,
        "error_msg_debug_sql": None,
        "error_msg_debug_python_code_data_visualization": None,
        "num_retries_debug_sql": 0,
        "num_retries_debug_python_code_data_visualization": 0
    }

    result = graph.invoke(initial_state, config=config)
    
    # Atualizar memória no session_state
    if "conversation_history" in result:
        st.session_state.conversation_history = result["conversation_history"]
    if "last_questions" in result:
        st.session_state.last_questions = result["last_questions"]
    
    return result

def process_visualization_data(viz_data: Dict[str, Any]) -> tuple:
    """Processa dados de visualização e retorna fig, df_viz, df_viz_dict"""
    fig_dict = viz_data.get("fig", None)
    df_viz_dict = viz_data.get("df_viz", None)
    
    # Converte DataFrame
    df_viz = None
    if df_viz_dict and 'data' in df_viz_dict and 'columns' in df_viz_dict:
        df_viz = pd.DataFrame(df_viz_dict['data'], columns=df_viz_dict['columns'])
    
    # Converte Figure
    fig = None
    if fig_dict and fig_dict.get('type') == 'Figure':
        fig = pio.from_json(fig_dict['json'])
    
    return fig, df_viz, df_viz_dict


def render_chat_message(message: Dict[str, Any]):
    """Renderiza uma mensagem do histórico"""
    role = message["role"]
    content = message["content"]
    
    with st.chat_message(role):
        st.markdown(content)
        
        # Renderiza elementos visuais se existirem (apenas para assistant)
        if role == "assistant":
            if "visualization_elements" in message:
                unique_id = str(uuid.uuid4())
                for i, element in enumerate(message["visualization_elements"]):
                    if element["type"] == "figure":
                        fig = pio.from_json(element["data"])
                        st.plotly_chart(fig, key=f"hist_fig_{unique_id}_{i}")
                    elif element["type"] == "dataframe":
                        df = pd.DataFrame(element["data"], columns=element["columns"])
                        st.dataframe(df, key=f"hist_df_{unique_id}_{i}")
            
            # Renderiza query SQL se existir
        if "sql_query" in message and message["sql_query"]:
            with st.expander("Query SQL", icon="🔍"):
                st.code(body=message["sql_query"], language="sql")


def handle_bot_response(prompt: str):
    """
    Adiciona o prompt do usuário ao histórico, executa o workflow,
    e adiciona a resposta do assistente ao histórico.
    """
    # Adiciona a mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Processa com LangGraph e exibe a resposta em tempo real
    with st.chat_message("assistant"):
        with st.spinner('Analisando sua solicitação... Por favor, aguarde.'):
            start_time = time.time()
            # Executa o workflow
            final_state = execute_workflow(prompt)

            end_time = time.time()
            processing_time = end_time - start_time

            # Processa a resposta de texto
            messages_list = final_state.get("messages", [])
            final_message = "Desculpe, tive um problema interno."
            if messages_list:
                last_message = messages_list[-1]
                # Se for um dict pega o content
                if isinstance(last_message, dict):
                    final_message = last_message.get('content', str(last_message))
                else:
                    # Se for um objeto AIMessage, pega o atributo content
                    final_message = getattr(last_message, 'content', str(last_message))

            st.markdown(final_message)
            
            # VERIFICAR SE HÁ VISUALIZAÇÕES
            visualization_elements = []
            sql_query = final_state.get("query", None)
            if "python_code_data_visualization" in final_state and final_state.get("python_code_validated"):
                try:
                    # Reconstrói DataFrame do estado
                    df_data = final_state.get("df_data", [])
                    df_columns = final_state.get("df_columns", [])
                    df = pd.DataFrame(df_data, columns=df_columns) if df_data else pd.DataFrame()
                    
                    # Executa o código Python
                    exec_globals = {"df": df, "pd": pd, "plotly": plotly, "go": go, "px": px, "plt": plt, "st": st}
                    exec(final_state.get("python_code_data_visualization", ""), exec_globals)
                    
                    # Renderiza os resultados
                    for key, value in exec_globals.items():
                        if key not in ['df', 'pd', 'plotly', 'go', 'px', 'plt', 'st']:
                            if isinstance(value, go.Figure):
                                visualization_elements.append({"type": "figure", "data": value.to_json()})
                            elif isinstance(value, pd.DataFrame):
                                visualization_elements.append({"type": "dataframe", "data": value.to_dict('records'), "columns": value.columns.tolist()})
                            # else:
                            #     st.write(f"{key}: {value}")
                                
                except Exception as e:
                    st.error(f"Erro ao executar visualização: {e}")

            for element in visualization_elements:
                if element["type"] == "figure":
                    fig = pio.from_json(element["data"])
                    st.plotly_chart(fig)
                elif element["type"] == "dataframe":
                    df = pd.DataFrame(element["data"], columns=element["columns"])
                    st.dataframe(df)

            # Mostra query SQL se existir
            else:
                if sql_query:
                    with st.expander("Query SQL", icon="🔍"):
                        st.code(body=sql_query, language="sql")
                        if final_state.get("explanation_query"):
                            st.write("Raciocionio da query:" + final_state.get("explanation_query"))
                    if final_state.get("python_code_data_visualization"):
                        with st.expander("Código Python", icon="🐍"):
                            st.code(body=final_state.get("python_code_data_visualization"), language="python")

            st.toast(f"Tempo de processamento: {processing_time:.2f} segundos")

            # Salva a resposta completa do assistente no histórico (simplificado)
            assistant_message = {
                "role": "assistant",
                "content": final_message,
                "python_code_validated": final_state.get("python_code_validated", False),
                "visualization_elements": visualization_elements,
                "sql_query": sql_query
            }

            st.session_state.messages.append(assistant_message)
            save_messages(st.session_state.messages, "messages.csv")


def render_header():
    """Renderiza o cabeçalho e os estilos CSS da página."""
    st.markdown("""
    <style>
        .stChatMessage {
            background-color: #F5F5F5 !important;
            border-radius: 30px;
            margin: 18px 1;
            padding: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>📊 Gerador de Relatórios Inteligente com IA</h1>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)


def render_chat_history():

    """Renderiza todas as mensagens do histórico, exceto a última do assistente."""
    for message in st.session_state.messages:
        render_chat_message(message)

def render_dataset_preview():
    """Container dedicado para visualizar o dataset"""
    df = pd.read_csv(dataset_path, sep=",", index_col=0)
    with st.expander("Clique para ver alguns dados da tabela", icon="📋"):
        st.dataframe(df)

def render_question_buttons():
    """Container dedicado para botões de perguntas sugeridas."""

    with st.expander("Dicas de perguntas", icon="💡"):
        suggested_questions = [
            "Os 5 diretores que mais fizeram filmes a partir de 2000",
            "Um gráfico de linhas mostrando o número de filmes lançados por ano",
            "Um gráfico de linhas mostrando o número de filmes lançados por ano a partir de 2000",
            "Número de filmes feitos nos Estados Unidos",
            "Número de filmes feitos por ano na Índia em gráfico de barras",
            "Quantos diretores americanos estão na lista?",
            "Número de filmes e diretores",
            "Os 5 países que mais fizeram filmes",
            "Quais país produziu mais filmes?", "Qual diretor produziu mais filmes?",
        ]
        
        for i in range(0, len(suggested_questions), 2):
                sub_col1, sub_col2 = st.columns(2)
                with sub_col1:
                    question1 = suggested_questions[i]
                    if st.button(question1, key=f"q_{i}", use_container_width=True):
                        st.session_state.pending_prompt = question1
                        st.info("Processando... Vá até o final da página para ver a resposta.")

                        st.rerun()
                        

                if i + 1 < len(suggested_questions):
                    with sub_col2:
                        question2 = suggested_questions[i+1]
                        if st.button(question2, key=f"q_{i+1}", use_container_width=True):
                            st.session_state.pending_prompt = question2
                            st.info("Processando... Vá até o final da página para ver a resposta.")

                            st.rerun()

def main_app():
    """Função principal que organiza e executa a aplicação."""

    try:
        # 1. Inicialização
        configure_page(layout="wide")
        initialize_session_state()
        configure_sidebar_with_button()
        remove_sidebar_navigation()
    except Exception as e:
        logger.error(f"Erro ao inicializar a aplicação: {e}")
        st.error(f"Erro ao inicializar a aplicação: {e}")
        st.stop()

    try:
    # 2. Renderiza a UI estática
        st.markdown("<div style='margin-top: 90px;'></div>", unsafe_allow_html=True)
        render_header()
        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        render_dataset_preview()
        render_question_buttons()

        # 3. Renderiza a UI dinâmica (histórico do chat)
        st.markdown("<div style='margin-top: 200px;'></div>", unsafe_allow_html=True)
        render_chat_history()

        if "pending_prompt" in st.session_state:
            prompt = st.session_state.pop("pending_prompt")
            handle_bot_response(prompt)
        

        # 4. Lida com a nova entrada do usuário
        if prompt := st.chat_input("Digite sua mensagem aqui..."):
            handle_bot_response(prompt)

    except Exception as e:
        logger.error(f"Erro ao renderizar a UI: {e}")
        st.error(f"Erro ao renderizar a UI: {e}")
        st.stop()
    
if __name__ == "__main__":
    # streamlit run src/frontend/pages/Chatbot.py
    main_app()