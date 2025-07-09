import streamlit as st
from datetime import datetime
from modules.frontend.styles import apply_main_styles
from modules.frontend.front import render_landing_page, render_analysis_page

def main():
    
    st.set_page_config(
        page_title="Python Code Analyzer",
        page_icon="🐍",
        layout="centered",
    )
    st.markdown(apply_main_styles(), unsafe_allow_html=True)
    st.session_state["parsing_complete"] = False

    if 'view' not in st.session_state:
        st.session_state.view = 'landing'

    if st.session_state.view == 'landing':
        render_landing_page()
    elif st.session_state.view == 'analysis':
        render_analysis_page()
    
    st.caption(f"Session started {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 