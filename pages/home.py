import os
import streamlit as st
from pages.custom_style import HEADER
from pages.uploders import upload_github_repo, upload_local_directory, upload_zip_file
from neo4j_driver import Neo4jDriver
from parsing_pipeline import load_codebase_into_neo4j
from pages.analytics import show_analytics_dashboard



def trigger_parse_again():
    st.session_state["parsing_completed"] = False
    st.session_state["start_parsing"] = True
    st.rerun()

if st.session_state.get("parsing_completed"):
    spacer, col1, col2,  = st.columns([3, 1, 1])
    with spacer: st.subheader("Codebase Analytics Dashboard")
    with col1: st.button(label="Create New Instance", use_container_width=True)
    with col2: st.button(label="Parse Again", use_container_width=True, on_click=trigger_parse_again)
    show_analytics_dashboard()

elif st.session_state.get("start_parsing"):
    driver = Neo4jDriver(
        uri=os.environ.get("NEO4J_URI"), 
        user=os.environ.get("NEO4J_USER"),
        password=os.environ.get("NEO4J_PASSWORD")
    )

    parsing_mode = st.session_state.get("selected_mode")
    codebase_path = st.session_state.get("codebase_path")

    if not(st.session_state.get("parsing_completed")) and codebase_path:
        with st.spinner(text="Parsing the code base and loading nodes into neo4 database.", show_time=True):
            completed = load_codebase_into_neo4j(codebase_path, parsing_mode)
        st.session_state["parsing_completed"] = completed
        st.rerun()

else:
    st.markdown(HEADER, unsafe_allow_html=True)
    
    st.subheader("Upload Your Codebase")
    col1, col2 = st.columns([1,1])
    with col1:
        options = ["Local Directory Path", "Codebase Zip File", "GitHub Repository Link"]
        selected_label = st.radio("Select Upload Method:", options=options, horizontal=True, key="upload_mode")
        selected_index = options.index(selected_label)
    with col2:
        modes = ["Custom Parsing", "LLM Parsing"]
        selected_mode_label = st.radio("Select Parsing Method:", options=modes, horizontal=True, key="parsing_mode")
        selected_mode = "llm" if selected_mode_label == "LLM Parsing" else None

    st.session_state["selected_mode"] = selected_mode
    uploader_functions = {
        0: upload_local_directory,
        1: upload_zip_file,
        2: upload_github_repo
    }
    uploader_functions[selected_index]()
    
    