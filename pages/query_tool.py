import os
import streamlit as st
from neo4j_driver import Neo4jDriver    
import streamlit.components.v1 as components
from CypherQAChain import chain
from utils import display_message

driver = Neo4jDriver(
    uri=os.environ.get("NEO4J_URI"), 
    user=os.environ.get("NEO4J_USER"),
    password=os.environ.get("NEO4J_PASSWORD")
)
DEFAULT_QUERY =  "MATCH (a)-[r]->(b) RETURN a, r, b"
message, type_ = None, None
def update_graph(cypher_query = None):
    print("query:", cypher_query)
    cypher_query =  cypher_query if cypher_query else DEFAULT_QUERY
    html_graph = driver.visualize_neo4j_graph(cypher_query)
    return html_graph

col1, col2 = st.columns([4, 1]) 
with col1:
    html_graph = update_graph(st.session_state.get("query"))
    components.html(html_graph, height=400)
    col1_inner, col2_inner = st.columns([8,1])
    with col1_inner:
        user_query = st.text_input(label="QUERY", label_visibility="collapsed", placeholder="Enter you query")
    with col2_inner:
        if st.button("RUN", use_container_width=True):
            try:
                result = chain.invoke(user_query)
                print("response", result)
                raw_cypher = result["intermediate_steps"][0]["query"]
                cypher_query = raw_cypher.replace("cypher", "").strip()
                st.session_state["query"] = cypher_query
                message, type_ = f"Cypher Query: `{result}`", "success"
            except Exception as e:
                print("Error:", e)
                st.error(f"Failed to generate Cypher: {e}")
    if message and type_:
        display_message(message, type_)
with col2:
    st.subheader("Node Types")
    st.markdown(
        ":red-badge[:material/category_search: Class] :green-badge[:material/data_object: Function] " \
        ":orange-badge[:material/variables: Variable] :blue-badge[:material/article: File]"
    )
    

