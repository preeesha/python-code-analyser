import streamlit as st

from modules.frontend.styles import apply_main_styles
from modules.retrival.query_pipeline import process_codebase_query
from modules.frontend.querybot import show_query_results
from modules.frontend.nodes_fromdb import render_graph_in_streamlit

st.set_page_config(page_title="Query Bot", page_icon="🤖", layout="wide")
st.markdown(apply_main_styles(), unsafe_allow_html=True)
st.title("🤖 Codebase Query Bot")

st.markdown("### Ask questions about your codebase")
st.markdown("*Ask natural language questions about your Python code structure, functions, classes, and relationships.*")

if not st.session_state.get("parsing_complete", False):
    st.warning("⚠️ **No codebase data found.** Please run the analysis from the Home page first.")
    st.info("💡 Once you've uploaded and analyzed your codebase, return here to ask questions about it.")
else:
    
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_query = st.text_input(
                "Your Question:",
                placeholder="e.g., 'Show me all functions that call the login method' or 'What classes inherit from BaseModel?'",
                help="Ask questions about functions, classes, imports, relationships, or any code structure in your project."
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True) 
            submit_query = st.button("🚀 Ask", use_container_width=True)

    if submit_query and user_query.strip():
        with st.spinner("🔍 Analyzing your question and querying the codebase..."):
            result = process_codebase_query(user_query)
        
        # Display results
        st.markdown("### 📋 Results")
        
        if result['success']:
            # Show the answer
            with st.container():
                st.markdown("**Answer:**")
                st.markdown(result['answer'])
            
            # Show graph if we have raw results
            if result.get('raw_results'):
                st.markdown("### 🕸️ Graph Visualization")
                try:
                    net = show_query_results(result['raw_results'])
                    
                    # Check if the network has any nodes
                    if hasattr(net, 'nodes') and len(net.nodes) > 0:
                        render_graph_in_streamlit(net)
                        st.success(f"✅ Graph created with {len(net.nodes)} nodes")
                    else:
                        st.warning("⚠️ No nodes were created for the graph. The data format might not be recognized.")
                        st.info("💡 Try queries like: 'Show me all imports from main.py' or 'What functions call each other?'")
                        
                except Exception as e:
                    st.error(f"❌ Error creating graph: {str(e)}")
                    st.info("💡 This might be because the query results don't contain relationship data.")
            else:
                st.info("ℹ️ No raw results available for graph visualization.")
                
            # Show the generated Cypher query
            if result.get('cypher_query'):
                with st.expander("🔧 Generated Cypher Query"):
                    st.code(result['cypher_query'], language="cypher")
        else:
            st.error(f"❌ {result['answer']}")
        
        # Add some spacing
        st.markdown("---")

    elif submit_query and not user_query.strip():
        st.warning("Please enter a question before clicking Ask!")
    
    st.markdown("---")
    st.markdown("*💡 **Tips:** Ask specific questions about your code structure. The more detailed your question, the better the results!*")