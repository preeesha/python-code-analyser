import streamlit as st
import os, json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import Counter, defaultdict
from neo4j_driver import Neo4jDriver

def load_analytics_data():
    try:
        with open('outputs/nodes.json', 'r') as f:
            nodes_data = json.load(f)
        with open('outputs/project_ast.json', 'r') as f:
            ast_data = json.load(f)
        driver = Neo4jDriver(
            uri=os.environ.get("NEO4J_URI"), 
            user=os.environ.get("NEO4J_USER"),
            password=os.environ.get("NEO4J_PASSWORD")
        )
        return nodes_data, ast_data, driver
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None

def create_overview_metrics(nodes_data, ast_data):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Total Files",
            value=ast_data.get('total_files', 0),
            delta=None,
            border=True
        )
    with col2:
        st.metric(
            label="Total Lines of Code",
            value=f"{ast_data.get('total_lines', 0):,}",
            delta=None,
            border=True
        )
    with col3:
        st.metric(
            label="Total Size",
            value=f"{ast_data.get('total_size_bytes', 0) / 1024:.1f} KB",
            delta=None,
            border=True
        )
    with col4:
        total_nodes = len(nodes_data)
        st.metric(
            label="Total Nodes",
            value=total_nodes,
            delta=None,
            border=True
        )

def analyze_node_types(nodes_data):
    node_types = [node['type'] for node in nodes_data]
    type_counts = Counter(node_types)
    return type_counts

def analyze_class_complexity(ast_data):
    classes_data = []
    for file_info in ast_data.get('files', []):
        classes = file_info.get('metadata', {}).get('classes', {})
        for class_name, class_info in classes.items():
            methods = class_info.get('methods', {})
            method_count = len(methods)
            
            total_variables = 0
            for method_info in methods.values():
                total_variables += len(method_info.get('variables', []))
            
            classes_data.append({
                'Class': class_name,
                'Methods': method_count,
                'Variables': total_variables,
                'File': file_info.get('relative_path', 'Unknown')
            })
    
    if classes_data:
        df = pd.DataFrame(classes_data)
        fig = px.scatter(
            df, 
            x='Methods', 
            y='Variables',
            size='Methods',
            color='Class',
            hover_data=['File'],
            title="Class Complexity Analysis",
            labels={'Methods': 'Number of Methods', 'Variables': 'Total Variables'}
        )
        
        return fig, df
    return None, None

def analyze_method_complexity(nodes_data):
    methods_data = []
    
    for node in nodes_data:
        if node['type'] == 'Function' and node['properties'].get('is_method', False):
            method_name = node['properties']['name']
            full_name = node['properties']['full_name']
            parameters = node['properties'].get('parameters', [])
            
            # Count related variables (local scope)
            related_vars = [n for n in nodes_data if n['type'] == 'Variable' and 
                          n['properties']['full_name'].startswith(full_name)]
            
            methods_data.append({
                'Method': method_name,
                'Full Name': full_name,
                'Parameters': len(parameters),
                'Local Variables': len(related_vars),
                'Complexity Score': len(parameters) + len(related_vars)
            })
    
    if methods_data:
        df = pd.DataFrame(methods_data)
        top_methods = df.nlargest(10, 'Complexity Score')
        
        fig = px.bar(
            top_methods,
            x='Complexity Score',
            y='Method',
            orientation='h',
            title="Top 10 Most Complex Methods",
            labels={'Complexity Score': 'Complexity Score (Parameters + Local Variables)'}
        )
        fig.update_layout(height=400)
        
        return fig, df
    return None, None

def create_file_statistics(ast_data):
    files_data = []
    for file_info in ast_data.get('files', []):
        files_data.append({
            'File': file_info.get('relative_path', 'Unknown'),
            'Lines': file_info.get('lines_count', 0),
            'Size (KB)': file_info.get('size_bytes', 0) / 1024,
            'Classes': len(file_info.get('metadata', {}).get('classes', {})),
            'Imports': len(file_info.get('metadata', {}).get('imports', []))
        })
    
    if files_data:
        df = pd.DataFrame(files_data)
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Lines of Code', 'File Size', 'Classes per File', 'Imports per File'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'bar'}]]
        )
        fig.add_trace(go.Bar(x=df['File'], y=df['Lines'], name='Lines'), row=1, col=1)
        fig.add_trace(go.Bar(x=df['File'], y=df['Size (KB)'], name='Size'), row=1, col=2)
        fig.add_trace(go.Bar(x=df['File'], y=df['Classes'], name='Classes'), row=2, col=1)
        fig.add_trace(go.Bar(x=df['File'], y=df['Imports'], name='Imports'), row=2, col=2)
        
        fig.update_layout(height=600, showlegend=False, title_text="File-Level Statistics")
        
        return fig, df
    return None, None



def show_analytics_dashboard():
    with st.spinner("Loading analytics data..."):
        nodes_data, ast_data, driver = load_analytics_data()
    if not nodes_data or not ast_data:
        st.error("Failed to load analytics data. Please ensure the files are available.")
        return
    
    create_overview_metrics(nodes_data, ast_data)
    tab1, tab2, tab3 = st.tabs(["🏗️ Structure", "📈 Complexity", "📁 Files"])
    
    with tab1:
        col1, spacer = st.columns(2)
        node_counts = analyze_node_types(nodes_data)
        with col1:
            st.subheader("Node Type Summary")
            node_df = pd.DataFrame(list(node_counts.items()), columns=['Type', 'Count'])
            st.dataframe(node_df, use_container_width=True, hide_index=True)
            
    with tab2:
        st.subheader("Complexity Analysis")
        class_fig, class_df = analyze_class_complexity(ast_data)
        if class_fig:
            st.plotly_chart(class_fig, use_container_width=True)
            
            if class_df is not None:
                with st.expander("Class Details"):
                    st.dataframe(class_df, use_container_width=True, hide_index=True)

        method_fig, method_df = analyze_method_complexity(nodes_data)
        if method_fig:
            st.plotly_chart(method_fig, use_container_width=True)

            if method_df is not None:
                with st.expander("Method Details"):
                    st.dataframe(method_df, use_container_width=True, hide_index=True)
        
    
    with tab3:
        st.subheader("File-Level Statistics")
        file_fig, file_df = create_file_statistics(ast_data)
        if file_fig:
            st.plotly_chart(file_fig, use_container_width=True)
            
            if file_df is not None:
                with st.expander("File Summary"):
                    st.dataframe(file_df, use_container_width=True)
    
    
    with st.expander("📋 Raw Data"):
        tab1, tab2 = st.tabs(["Nodes Data", "AST Data"])
        with tab1: st.json(nodes_data)
        with tab2: st.json(ast_data)
    