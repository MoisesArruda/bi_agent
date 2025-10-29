import os, sys
import streamlit as st
import streamlit_authenticator as stauth
import logging
from time import sleep

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Adiciona o diretório raiz ao sys.path para importar módulos
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(project_root)

from src.frontend.page_config  import remove_sidebar_navigation, configure_page, configure_sidebar
from src.frontend.utils.utils import load_users, save_users

def config_register_page():
    """
    Configura a página de registro de usuário.
    """
    configure_page(page_title="Registro de Usuário", page_icon="📝", layout="centered", initial_sidebar_state="expanded")

    config = load_users()

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )

    configure_sidebar()
    remove_sidebar_navigation() # Esconde o MultiPages

    try:
        if authenticator.register_user("Cadastro", preauthorization=False):
            save_users(config)
            st.success("Usuário registrado com sucesso!")
            
            with st.spinner("Aguarde..."):
                sleep(3)
            st.switch_page("pages/Login.py")

    except Exception as e:
        logging.error(f"Erro durante o registro: {e}")
        st.error(f"Erro durante o registro: {e}")

if __name__ == "__main__":
    config_register_page()