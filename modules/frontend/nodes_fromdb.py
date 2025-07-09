from pyvis.network import Network
import networkx as nx
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from modules.frontend.utils import get_color_map
import streamlit as st
from streamlit.components.v1 import html


load_dotenv(override=True)

NEO4J_USERNAME="neo4j"
driver = GraphDatabase.driver(os.getenv("NEO4J_URI"), auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")))

if driver.verify_connectivity():
    print("Connected to Neo4j")
else:
    print("Failed to connect to Neo4j")

def get_full_codebase():
    with driver.session() as session:
        query = """
        MATCH (n)-[r]->(m)
        RETURN 
            ID(n) AS source_id,
            n.name AS source_name,
            labels(n)[0] AS source_label,
            ID(m) AS target_id,
            m.name AS target_name,
            labels(m)[0] AS target_label,
            type(r) AS relation
        """
        result = session.run(query)
        return result.data()
    
def fetch_all_nodes():
    with driver.session() as session:
        result = session.run("""
        MATCH (n)
        RETURN 
            ID(n) AS node_id,
            n.name AS name,
            labels(n)[0] AS label
        """)
        return [record.data() for record in result]
    


def build_network_graph(data):
    net = Network( height="500px",width="100%", bgcolor="#1a1a1a", font_color="white", directed=True)
    added_nodes = set()
    
    for record in data:
        src_id = record['source_id']
        src_name = record['source_name']
        src_label = record['source_label']
        
        tgt_id = record['target_id']
        tgt_name = record['target_name']
        tgt_label = record['target_label']
        
        relation = record['relation']
        
        if src_id not in added_nodes:
            net.add_node(src_id, label=src_name, title=f"Type: {src_label}", color=get_color_map("parsed_code").get(src_label))
            added_nodes.add(src_id)
            
        if tgt_id not in added_nodes:
            net.add_node(tgt_id, label=tgt_name, title=f"Type: {tgt_label}", color=get_color_map("parsed_code").get(tgt_label))
            added_nodes.add(tgt_id)
            
        net.add_edge(src_id, tgt_id, label=relation, color="#888")
     
    return net

def render_graph_in_streamlit(net: Network):
    net.save_graph("graph.html")
    with open("graph.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    # Inject CSS to remove the border and set the body background
    custom_css = (
        "<style>"
        "body { margin: 0; background-color: #1a1a1a; height: 500px; }"
        ".vis-network { border: none !important; }"
        "</style>"
    )

    if "</head>" in html_content:
        html_content = html_content.replace("</head>", f"{custom_css}</head>")
    else:
        html_content = custom_css + html_content

    html(html_content, height=500, width=900)
   
   