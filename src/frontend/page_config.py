import os
import logging
import streamlit as st
from dotenv import load_dotenv
import yaml
from yaml.loader import SafeLoader

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

sidebar_logo = os.path.join(os.path.dirname(__file__), "img", 'Logo-Arruda-Consulting.png')

def remove_sidebar_navigation() -> None:
    """
    Esconde os módulos da barra lateral.
    """
    no_sidebar_style = """
        <style>
            div[data-testid="stSidebarNav"] {display: none;}
        </style>
    """
    st.markdown(no_sidebar_style, unsafe_allow_html=True)

def configure_sidebar():
    """
    Monta a barra lateral com informações institucionais e orientações de uso.
    """

    st.sidebar.image(image=sidebar_logo, width=250, use_container_width=True)
    st.sidebar.markdown("---")

    st.sidebar.title("Sobre o Sistema")
    st.sidebar.info(
        """Esta ferramenta utiliza inteligência artificial para apoiar a análise de dados,
        geração de gráficos e revisão de tabelas de forma automatizada."""
    )

    st.sidebar.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

def configure_sidebar_with_button():
    """
    Adiciona um botão de limpeza de histórico de mensagens ao sidebar.
    """

    st.sidebar.image(image=sidebar_logo, width=250, use_container_width=False)
    st.sidebar.markdown("---")

    if st.sidebar.button(icon="🧹", label="Limpar histórico", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Olá! Sou sua assistente para análise de dados. Como posso te ajudar hoje?"}
        ]

def configure_page(layout: str = "wide", initial_sidebar_state: str = "auto", page_title: str = "AI Agent Arruda Consulting", page_icon: str = sidebar_logo):
    """
    Configura a página.
    """
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state=initial_sidebar_state,        
    )

def apply_login_styles():
    """
    Aplica estilos CSS personalizados para a página de login.
    """
    
    login_styles = """
        
<style>
        .main .block-container {
            background: linear-gradient(135deg, #1e3a8a, #0f172a);
            padding: 3rem;
            border-radius: 15px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
            max-width: 500px;
            margin: auto;
            color: #f3f4f6;
        }

        .logo-container {
            text-align: center;
            margin-bottom: 2rem;
        }

        .logo-container img {
            width: 120px;
            border-radius: 50%;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
        }

        .stTextInput > div > input {
            background-color: #1e293b;
            color: #f3f4f6;
            border: 1px solid #64748b;
            border-radius: 8px;
            padding: 0.75rem;
        }

        .stTextInput > div > input::placeholder {
            color: #94a3b8;
        }

        .stButton > button {
            width: 100%;
            background: linear-gradient(to right, #10b981, #22d3ee);
            color: white;
            border: none;
            padding: 0.75rem;
            border-radius: 8px;
            font-weight: bold;
            transition: background 0.3s ease;
        }

        .stButton > button:hover {
            background: linear-gradient(to right, #059669, #0ea5e9);
        }

        .forgot-password {
            text-align: center;
            margin-top: 1rem;
            color: #94a3b8;
            font-size: 0.9rem;
        }

        .forgot-password a {
            color: #38bdf8;
            text-decoration: none;
        }

        .forgot-password a:hover {
            text-decoration: underline;
        }

    </style>
    """
    st.markdown(login_styles, unsafe_allow_html=True)
