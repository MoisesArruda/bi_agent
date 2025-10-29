import os
import sys
from dotenv import load_dotenv
import streamlit as st
import streamlit_authenticator as stauth
import logging

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(project_root)

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from src.frontend.page_config import remove_sidebar_navigation, configure_sidebar, configure_page, apply_login_styles
from src.frontend.utils.utils import load_users

image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "img", 'ArrudaConsulting.jpeg')

configure_page(page_title="Login - Arruda Consulting", page_icon="🔐")
apply_login_styles()

configure_sidebar()
remove_sidebar_navigation()

config = load_users()

authenticator = stauth.Authenticate(
config["credentials"],
config["cookie"]["name"],
config["cookie"]["key"],
config["cookie"]["expiry_days"],
)

def config_login_page():
    """
    Configura a página de login.
    """
    st.markdown("<p style='text-align: center; color: #6b7280; font-size: 0.8rem;'>© 2025 Arruda Consulting</p>", unsafe_allow_html=True)
    
    # Container principal
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col2:
            st.markdown('<div class="logo-container">', unsafe_allow_html=True)

        try:
            # Formulário de login personalizado com placeholders
            with st.form("login_form"):
                st.markdown("### Login")
                username = st.text_input("Username", placeholder="admin")
                password = st.text_input("Password", type="password", placeholder="123")
                submitted = st.form_submit_button("Login")
                
                if submitted:
                    # Verificar credenciais
                    if username == "admin" and password == "123":
                        session_state = st.session_state
                        session_state.is_logged_in = True
                        session_state.current_username = "admin"
                        logging.info("Usuário admin autenticado com sucesso.")
                        with st.spinner("Redirecionando para a página de chat..."):
                            st.switch_page("pages/Chatbot.py")
                    else:
                        st.error("Username/senha incorreto.")

        except Exception as e:
            logging.error(f"Erro durante o login: {str(e)}")
            st.error("Tente novamente. Ocorreu um erro durante o login.")

        col1, col2 = st.columns([2, 8])
        with col1:
            if st.button("Registrar", use_container_width=True):
                logging.info("Redirecionando para a página de registro.")
                st.switch_page("pages/Register.py")
        with col2:
            if st.button("Esqueci minha senha", use_container_width=True):
                logging.info("Botão 'Esqueci minha senha' clicado.")
                st.info("Funcionalidade de recuperação de senha em desenvolvimento.")


if __name__ == "__main__":
    config_login_page()