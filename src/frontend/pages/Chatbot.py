import streamlit as st
import os, sys
import logging
import uuid
import plotly.io as pio
import pandas as pd
import uuid
from typing import Dict, Any
import csv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(project_root)

from src.frontend.page_config import hide_navigation_sidebar, page_config, side_navbar_with_button
from src.infrastructure.llm_providers.groq.client import GroqChatHandler

image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "img", 'ArrudaConsulting.jpeg')
dataset_path = os.path.join(project_root, "data", "dataset", "netflix_movies_and_tv_shows.csv")

groq_client = GroqChatHandler()


def initialize_session_state():
    """Inicialização mínima necessária"""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Olá! Sou a GUIA, sua assistente para análise de dados. Como posso te ajudar hoje?"}
        ]

def execute_workflow(prompt: str) -> Dict[str, Any]:
    """Executa o workflow e retorna o estado final"""

    invoke_model = groq_client.get_model("openai/gpt-oss-120b")
    response = invoke_model.invoke(prompt)
    return response

    # unique_thread_id = str(uuid.uuid4())
    # response = groq_client.send_message("Olá. Com qual modelo estou conversando?")
    # config = {"configurable": {"thread_id": unique_thread_id}}
    # return graph.invoke({"question": prompt}, config=config)

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
            if "fig" in message and message["fig"]:
                st.plotly_chart(message["fig"])
            elif "dataframe" in message and message["dataframe"]:
                df_dict = message["dataframe"]
                if df_dict and 'data' in df_dict and 'columns' in df_dict:
                    df = pd.DataFrame(df_dict['data'], columns=df_dict['columns'])
                    st.dataframe(df)


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
            # Executa o workflow
            final_state = execute_workflow(prompt)

            # Processa a resposta de texto
            messages_list = final_state.content
            final_message = messages_list
            # messages_list = final_state.invoke(prompt)
            # messages_list = final_state.get("messages", [])
            # final_message = "Desculpe, tive um problema interno."
            # if messages_list:
            #     last_message = messages_list[-1]
            #     final_message = getattr(last_message, 'content', str(last_message))

            # Processa os dados de visualização (gráficos, tabelas)
            fig = None
            df_viz = None
            df_viz_dict = None
            # viz_data = final_state.get("python_code_store_variables_dict", {})
            # fig, df_viz, df_viz_dict = process_visualization_data(viz_data)

            # Renderiza a resposta de texto e visual
            st.markdown(final_message)
            if fig is not None:
                st.plotly_chart(fig)
            elif df_viz is not None:
                st.dataframe(df_viz)

            # Salva a resposta completa do assistente no histórico
            assistant_message = {
                "role": "assistant",
                "content": final_message,
                "fig": fig,
                "dataframe": df_viz_dict,
            }

            st.session_state.messages.append(assistant_message)
            # save_messages(st.session_state.messages, "src/app/data/historic_data.csv")


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

def render_dataset_preview():
    """Container dedicado para botões de perguntas sugeridas."""
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
                if st.button(question1, key=f"sidebar_q_{i}", use_container_width=True):
                    st.session_state.pending_prompt = question1
                    st.rerun()
                    
            if i + 1 < len(suggested_questions):
                with sub_col2:
                    question2 = suggested_questions[i+1]
                    if st.button(question2, key=f"sidebar_q_{i+1}", use_container_width=True):
                        st.session_state.pending_prompt = question2
                        st.rerun()
                            
def render_chat_history():

    """Renderiza todas as mensagens do histórico, exceto a última do assistente."""
    # A lógica de renderizar a última mensagem já está em handle_bot_response
    for message in st.session_state.messages:
        render_chat_message(message)

def main_app():
    """Função principal que organiza e executa a aplicação."""

    # 1. Inicialização
    page_config(layout="wide")
    initialize_session_state()
    side_navbar_with_button()
    hide_navigation_sidebar()

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
    
if __name__ == "__main__":
    main_app()