import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import json
import time
from datetime import datetime
import random

# Configure page
st.set_page_config(
    page_title="CodeGraph AI",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .query-box {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .status-success {
        background: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .status-processing {
        background: #fff3cd;
        color: #856404;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
    .code-snippet {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        border-left: 3px solid #667eea;
        font-family: 'Courier New', monospace;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'project_loaded' not in st.session_state:
    st.session_state.project_loaded = False
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'current_graph_data' not in st.session_state:
    st.session_state.current_graph_data = None
if 'project_stats' not in st.session_state:
    st.session_state.project_stats = {}

# Header
st.markdown("""
<div class="main-header">
    <h1>🕸️ CodeGraph AI</h1>
    <p>Intelligent Python Code Analysis & Visualization</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for project management
with st.sidebar:
    st.header("📁 Project Management")
    
    # Project upload/selection
    project_source = st.radio(
        "Select Project Source:",
        ["Upload Directory", "GitHub Repository", "Local Path"]
    )
    
    if project_source == "Upload Directory":
        uploaded_files = st.file_uploader(
            "Upload Python files",
            type=['py'],
            accept_multiple_files=True,
            help="Upload multiple Python files from your project"
        )
        
        if uploaded_files and st.button("🔄 Process Files"):
            # Simulate processing
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            st.session_state.project_loaded = True
            st.session_state.project_stats = {
                'files': len(uploaded_files),
                'classes': random.randint(15, 50),
                'functions': random.randint(100, 300),
                'variables': random.randint(200, 500),
                'connections': random.randint(150, 400)
            }
            st.success("✅ Project processed successfully!")
    
    elif project_source == "GitHub Repository":
        repo_url = st.text_input("GitHub Repository URL", placeholder="https://github.com/user/repo")
        branch = st.text_input("Branch", value="main")
        
        if repo_url and st.button("🔄 Clone & Process"):
            with st.spinner("Cloning repository..."):
                time.sleep(2)
            st.session_state.project_loaded = True
            st.session_state.project_stats = {
                'files': random.randint(20, 80),
                'classes': random.randint(25, 70),
                'functions': random.randint(150, 400),
                'variables': random.randint(300, 700),
                'connections': random.randint(200, 600)
            }
            st.success("✅ Repository processed successfully!")
    
    else:  # Local Path
        local_path = st.text_input("Local Directory Path", placeholder="/path/to/project")
        
        if local_path and st.button("🔄 Process Directory"):
            with st.spinner("Processing directory..."):
                time.sleep(1.5)
            st.session_state.project_loaded = True
            st.session_state.project_stats = {
                'files': random.randint(30, 100),
                'classes': random.randint(20, 60),
                'functions': random.randint(200, 500),
                'variables': random.randint(400, 800),
                'connections': random.randint(300, 700)
            }
            st.success("✅ Directory processed successfully!")
    
    # Project Statistics
    if st.session_state.project_loaded:
        st.subheader("📊 Project Statistics")
        stats = st.session_state.project_stats
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Files", stats['files'])
            st.metric("Classes", stats['classes'])
        with col2:
            st.metric("Functions", stats['functions'])
            st.metric("Variables", stats['variables'])
        
        st.metric("Connections", stats['connections'])
        
        # Analysis Options
        st.subheader("🔧 Analysis Options")
        
        include_private = st.checkbox("Include Private Methods", value=True)
        include_imports = st.checkbox("Include Import Relationships", value=True)
        depth_limit = st.slider("Relationship Depth", 1, 5, 3)
        
        # Export Options
        st.subheader("📤 Export Options")
        if st.button("Export Graph Data"):
            st.download_button(
                label="Download JSON",
                data=json.dumps({"nodes": [], "edges": []}, indent=2),
                file_name="codegraph_data.json",
                mime="application/json"
            )

# Main content area
if not st.session_state.project_loaded:
    st.info("👈 Please load a project from the sidebar to begin analysis.")
    
    # Show example queries
    st.subheader("🔍 Example Queries")
    
    example_queries = [
        "Show me all classes that inherit from BaseModel",
        "Find functions that call the database",
        "What are the dependencies of the UserService class?",
        "Show me the data flow for user authentication",
        "Which functions have the highest complexity?",
        "Find all classes with circular dependencies"
    ]
    
    cols = st.columns(2)
    for i, query in enumerate(example_queries):
        with cols[i % 2]:
            st.markdown(f"**{query}**")
    
else:
    # Natural Language Query Interface
    st.subheader("💬 Ask CodeGraph AI")
    
    # Query input
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_query = st.text_input(
            "Enter your question about the codebase:",
            placeholder="e.g., Show me all classes that inherit from BaseClass",
            key="query_input"
        )
    
    with col2:
        query_button = st.button("🔍 Query", type="primary")
    
    # Predefined query buttons
    st.markdown("**Quick Queries:**")
    query_cols = st.columns(4)
    
    quick_queries = [
        "Show class hierarchy",
        "Find circular dependencies", 
        "Show data flow",
        "Analyze complexity"
    ]
    
    for i, q in enumerate(quick_queries):
        with query_cols[i]:
            if st.button(q, key=f"quick_{i}"):
                user_query = q
                query_button = True
    
    # Process query
    if query_button and user_query:
        # Add to history
        st.session_state.query_history.append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'query': user_query,
            'status': 'completed'
        })
        
        # Show processing status
        with st.spinner("🧠 Processing your query..."):
            time.sleep(1)
        
        # Create mock graph data
        def create_mock_graph():
            # Create a sample graph based on the query
            nodes = []
            edges = []
            
            # Sample nodes
            sample_nodes = [
                {'id': 'UserService', 'label': 'UserService', 'type': 'class', 'file': 'user_service.py'},
                {'id': 'DatabaseManager', 'label': 'DatabaseManager', 'type': 'class', 'file': 'db_manager.py'},
                {'id': 'AuthService', 'label': 'AuthService', 'type': 'class', 'file': 'auth_service.py'},
                {'id': 'login', 'label': 'login()', 'type': 'function', 'file': 'auth_service.py'},
                {'id': 'validate_user', 'label': 'validate_user()', 'type': 'function', 'file': 'user_service.py'},
                {'id': 'connect_db', 'label': 'connect_db()', 'type': 'function', 'file': 'db_manager.py'},
            ]
            
            # Sample edges
            sample_edges = [
                {'from': 'AuthService', 'to': 'UserService', 'type': 'imports'},
                {'from': 'UserService', 'to': 'DatabaseManager', 'type': 'uses'},
                {'from': 'login', 'to': 'validate_user', 'type': 'calls'},
                {'from': 'validate_user', 'to': 'connect_db', 'type': 'calls'},
            ]
            
            return sample_nodes, sample_edges
        
        nodes, edges = create_mock_graph()
        
        # Display results
        st.success("✅ Query processed successfully!")
        
        # Show generated Cypher query
        with st.expander("🔍 Generated Cypher Query"):
            cypher_query = f"""
MATCH (n)-[r]-(m)
WHERE n.name CONTAINS '{user_query.split()[-1] if user_query.split() else 'class'}'
RETURN n, r, m
LIMIT 50
"""
            st.code(cypher_query, language='cypher')
        
        # Visualization
        st.subheader("📊 Graph Visualization")
        
        # Create network graph using Plotly
        fig = go.Figure()
        
        # Add nodes
        node_x = [random.uniform(0, 10) for _ in nodes]
        node_y = [random.uniform(0, 10) for _ in nodes]
        
        # Color mapping for node types
        color_map = {'class': '#FF6B6B', 'function': '#4ECDC4', 'variable': '#45B7D1'}
        
        for i, node in enumerate(nodes):
            fig.add_trace(go.Scatter(
                x=[node_x[i]], 
                y=[node_y[i]],
                mode='markers+text',
                marker=dict(
                    size=20,
                    color=color_map.get(node['type'], '#95A5A6'),
                    line=dict(width=2, color='white')
                ),
                text=node['label'],
                textposition="middle center",
                textfont=dict(color='white', size=10),
                hovertemplate=f"<b>{node['label']}</b><br>Type: {node['type']}<br>File: {node['file']}<extra></extra>",
                showlegend=False
            ))
        
        # Add edges
        for edge in edges:
            from_idx = next(i for i, n in enumerate(nodes) if n['id'] == edge['from'])
            to_idx = next(i for i, n in enumerate(nodes) if n['id'] == edge['to'])
            
            fig.add_trace(go.Scatter(
                x=[node_x[from_idx], node_x[to_idx]],
                y=[node_y[from_idx], node_y[to_idx]],
                mode='lines',
                line=dict(width=2, color='rgba(125, 125, 125, 0.5)'),
                hoverinfo='none',
                showlegend=False
            ))
        
        fig.update_layout(
            title=f"Code Graph: {user_query}",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ 
                dict(
                    text="Interactive Code Graph - Hover over nodes for details",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(color='#888', size=12)
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Analysis Results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Analysis Results")
            
            # Mock analysis results
            results_data = {
                'Metric': ['Nodes Found', 'Relationships', 'Max Depth', 'Complexity Score'],
                'Value': [len(nodes), len(edges), 3, 7.2]
            }
            
            results_df = pd.DataFrame(results_data)
            st.dataframe(results_df, use_container_width=True, hide_index=True)
            
            # Show insights
            st.subheader("💡 Key Insights")
            insights = [
                "AuthService has high coupling with UserService",
                "DatabaseManager is a critical dependency",
                "No circular dependencies detected",
                "Average function complexity: Medium"
            ]
            
            for insight in insights:
                st.markdown(f"• {insight}")
        
        with col2:
            st.subheader("🎯 Affected Components")
            
            # Mock component list
            components = [
                {'name': 'UserService.py', 'impact': 'High', 'lines': 245},
                {'name': 'AuthService.py', 'impact': 'Medium', 'lines': 156},
                {'name': 'DatabaseManager.py', 'impact': 'High', 'lines': 189},
                {'name': 'utils.py', 'impact': 'Low', 'lines': 78}
            ]
            
            for comp in components:
                impact_color = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}
                st.markdown(f"{impact_color[comp['impact']]} **{comp['name']}** ({comp['lines']} lines)")
            
            # Code snippet
            st.subheader("📋 Related Code")
            st.code("""
class UserService:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def validate_user(self, username):
        return self.db.query_user(username)
            """, language='python')

# Query History
if st.session_state.query_history:
    st.subheader("📚 Query History")
    
    history_df = pd.DataFrame(st.session_state.query_history)
    st.dataframe(history_df, use_container_width=True, hide_index=True)
    
    if st.button("🗑️ Clear History"):
        st.session_state.query_history = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p>🕸️ CodeGraph AI - Powered by Neo4j & LangGraph</p>
    <p>Transform your codebase into interactive knowledge graphs</p>
</div>
""", unsafe_allow_html=True)