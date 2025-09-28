import os, sys
import logging
from dotenv import load_dotenv
import streamlit as st
import streamlit_authenticator as stauth

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(project_root)

from src.frontend.page_config import hide_navigation_sidebar, load_users, side_navbar, page_config

image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "img", 'ArrudaConsulting.jpeg')

page_config(page_title="Login - Arruda Consulting", page_icon="🔐")

side_navbar()
hide_navigation_sidebar()

config = load_users()

authenticator = stauth.Authenticate(
config["credentials"],
config["cookie"]["name"],
config["cookie"]["key"],
config["cookie"]["expiry_days"],
)


# CSS personalizado para estilizar a página
st.markdown("""
<style>
        .main .block-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        max-width: 150px; /* O layout="centered" já ajuda com isso */
    }
    
    .logo-container {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .stButton > button {
        width: 100%;
        background-color: #dc2626;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #b91c1c;
    }
    
    .forgot-password {
        text-align: center;
        margin-top: 1rem;
        color: #6b7280;
    }
    
    .placeholder-image {
        background-color: #e5e7eb;
        border: 2px dashed #9ca3af;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        color: #6b7280;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def login():
    
    # Container principal
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="logo-container">', unsafe_allow_html=True)
            # st.image(str(image_path), width=100, use_container_width=True)

        try:

            name = authenticator.login("Login", "main")
            session_state = st.session_state
            session_state.is_logged_in = False

            if st.session_state["authentication_status"]:
                session_state.is_logged_in = True
                session_state.current_username = name
                logging.info(f"Usuário {name} autenticado com sucesso.")
                with st.spinner("Redirecionando para a página de chat..."):
                    st.switch_page("pages/Chatbot.py")

            elif st.session_state["authentication_status"] == False:
                session_state.is_logged_in = False
                st.error("Username/senha incorreto.")

            elif st.session_state["authentication_status"] is None:
                session_state.is_logged_in = False
                st.warning("Por favor, digite seu usuário e senha.")

        except Exception as e:
            logging.error(f"Erro durante o login: {str(e)}")
            st.error("Ocorreu um erro durante o login. Por favor, tente novamente.")

        col1, col2 = st.columns([2, 8])
        with col1:
            if st.button("Registrar", use_container_width=True):
                logging.info("Redirecionando para a página de registro.")
                st.switch_page("pages/Register.py")
        with col2:
            if st.button("Esqueci minha senha", use_container_width=True):
                logging.info("Botão 'Esqueci minha senha' clicado.")
                st.info("Funcionalidade de recuperação de senha em desenvolvimento.")

    # Rodapé

    st.markdown("<p style='text-align: center; color: #6b7280; font-size: 0.8rem;'>© 2025 Arruda Consulting</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    login()