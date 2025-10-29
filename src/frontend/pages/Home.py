import streamlit as st
import os, sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(project_root)

from src.frontend.page_config import remove_sidebar_navigation, configure_sidebar

image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "img", 'mermaid.png')


def home_page():
    
    st.markdown("""
        <style>
        .stButton button {
            width: 80%;
            height: 50px;
            font-size: 50px;
            font-weight: bold;
        }

        </style>
    """, unsafe_allow_html=True)
    
    configure_sidebar()
    remove_sidebar_navigation()

    st.markdown('<div class="centered">', unsafe_allow_html=True)
    st.title("Solução completa de Inteligência Artificial para análise de dados")

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    col1,col2,col3 = st.columns([1,2,1])
    with col2:
        if st.button("Login"):
            st.session_state["pagina_atual"] = "Login"
            st.switch_page("pages/Login.py")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="centered">', unsafe_allow_html=True)
    st.image(image_path, width=300, use_container_width=True)
            
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    home_page()