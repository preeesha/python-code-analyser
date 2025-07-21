import streamlit as st
from modules.frontend.nodes_fromdb import get_full_codebase, build_network_graph, render_graph_in_streamlit


st.set_page_config(page_title="Codebase Visualizer", page_icon="📊", layout="wide")
st.title("📊 Codebase Visualizer")

st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    .stApp {
        background-color: #1a1a1a;
    }
    .main {
        background-color: #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)

if st.session_state.get("parsing_complete", False):
    
    col1, col2, col3 = st.columns([1, 8, 1])
    
    with col2:
        
        with st.container():
            st.markdown("### Interactive Codebase Graph")
           
           
            data = get_full_codebase()  
            net = build_network_graph(data, height="80vh", width="100%")  
            
            render_graph_in_streamlit(net, height=800, width=1200)
else:
    st.info("No analytics data is available. Run the analysis from the Home page first.")