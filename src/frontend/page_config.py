import os
import logging
import streamlit as st
from dotenv import load_dotenv
import yaml
from yaml.loader import SafeLoader

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

sidebar_image = os.path.join(os.path.dirname(__file__), "img", 'GrupoUnimetal.png')

def page_config(layout: str = "wide", initial_sidebar_state: str = "auto"):

    st.set_page_config(
        page_title="AI Agent Unimetal",
        page_icon=sidebar_image,
        layout=layout,
        initial_sidebar_state=initial_sidebar_state,        
    )

def side_navbar():
    """
    Configura a barra lateral da aplicação Streamlit.
    Esta função adiciona:
    - Título da barra lateral
    - Informações sobre a AInvest
    - Diretrizes de uso
    - Avisos importantes sobre o monitoramento

    Returns:
    None
    """

    st.sidebar.image(image=sidebar_image, width=250, use_container_width=False)
    st.sidebar.markdown("---")

    st.sidebar.title("Informações")
    st.sidebar.info(
        """A GUIA é uma aplicação que utiliza inteligência artificial e que foi desenvolvida para 
                    auxiliar na geração e revisão de dados e tabelas. """
    )
    
    st.sidebar.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

# Esconde o MultiPages
def hide_navigation_sidebar() -> None:

    no_sidebar_style = """
        <style>
            div[data-testid="stSidebarNav"] {display: none;}
        </style>
    """
    st.markdown(no_sidebar_style, unsafe_allow_html=True)


def load_users() -> dict:

    yaml_path = "src/frontend/users/config.yaml"
    with open(yaml_path, "r") as file:
        config = yaml.load(file, Loader=SafeLoader)
    logging.info("Usuários carregados com sucesso do arquivo 'config.yaml'")

    return config

def save_users(config: dict) -> None:

    yaml_path = "src/frontend/users/config.yaml"
    with open(yaml_path, "w") as file:
        yaml.dump(config, file, default_flow_style=False)
    logging.info("Usuários salvos com sucesso no arquivo 'config.yaml'")


def main():
    page_config()
    side_navbar()

if __name__ == "__main__":
    main()