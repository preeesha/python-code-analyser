import streamlit as st
from modules.frontend.nodes_fromdb import get_full_codebase, build_network_graph, render_graph_in_streamlit
st.set_page_config(page_title="Codebase Visualizer", page_icon="📊", layout="wide")
st.title("📊 Codebase Visualizer")

if st.session_state.get("parsing_complete", False):
    data = get_full_codebase()  # from Neo4j
    net =  build_network_graph(data) # build PyVis graph
    render_graph_in_streamlit(net)    
else:
    st.info("No analytics data is available. Run the analysis from the Home page first.")