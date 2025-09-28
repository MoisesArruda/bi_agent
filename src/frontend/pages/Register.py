import os, sys
from time import sleep
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_extras.switch_page_button import switch_page
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Adiciona o diretório raiz ao sys.path para importar módulos
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(project_root)

from src.frontend.page_config  import hide_navigation_sidebar, load_users, save_users, side_navbar

def register_page():
    st.set_page_config(
        page_title="Registro de Usuário",
        page_icon="📝",
        layout="centered",
        initial_sidebar_state="expanded",
    )

    config = load_users()

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )

    side_navbar()
    hide_navigation_sidebar() # Esconde o MultiPages

    try:
        if authenticator.register_user("Cadastro", preauthorization=False):
            save_users(config)
            st.success("Usuário registrado com sucesso!")
            
            with st.spinner("Aguarde..."):
                sleep(3)
            st.switch_page("pages/Login.py")

    except Exception as e:
        logging.error(f"Erro durante o registro: {e}")
        st.error("Por favor, preencha todos os campos.")

if __name__ == "__main__":
    register_page()