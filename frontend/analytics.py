import streamlit as st
import json
import pandas as pd
import plotly.express as px
from pathlib import Path

def read_parse_data(file_path: Path) -> dict:
    """Safely read and parse the JSON data file."""
    if not file_path.exists():
        return {}
    with open(file_path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(f"❌ Analytics error: Could not decode the JSON file `{file_path}`.")
            return {}

def plot_node_distribution(df_nodes: pd.DataFrame):
    """Display a bar chart of node types."""
    st.markdown("#### 🧐 Node Type Distribution")
    st.write("This chart shows the counts of different types of code structures (nodes) found in the project, such as functions, classes, and variables.")
    
    node_counts = df_nodes['type'].value_counts().reset_index()
    node_counts.columns = ['Node Type', 'Count']
    
    fig = px.bar(
        node_counts, 
        x='Node Type', 
        y='Count', 
        title="Distribution of Node Types",
        color='Node Type',
        template='streamlit'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_relationship_distribution(df_relationships: pd.DataFrame):
    """Display a bar chart of relationship types."""
    st.markdown("#### 🔗 Relationship Type Distribution")
    st.write("This chart illustrates how different parts of the code are connected. For example, `CALLS` shows function calls, and `IMPORTS` shows module dependencies.")
    
    relationship_counts = df_relationships['relationship_type'].value_counts().reset_index()
    relationship_counts.columns = ['Relationship Type', 'Count']
    
    fig = px.bar(
        relationship_counts, 
        x='Relationship Type', 
        y='Count', 
        title="Distribution of Relationship Types",
        color='Relationship Type',
        template='streamlit'
    )
    st.plotly_chart(fig, use_container_width=True)

def show_file_complexity(df_nodes: pd.DataFrame):
    """Display a table with file complexity metrics."""
    st.markdown("#### 🗂️ File Complexity Analysis")
    st.write("This table breaks down the number of classes and functions in each file, helping to identify more complex parts of the codebase.")

    # Filter for functions and classes and ensure 'file_path' exists
    df_filtered = df_nodes[df_nodes['type'].isin(['Function', 'Class'])].copy()
    
    # Extract file name from properties
    df_filtered['file_name'] = df_filtered['properties'].apply(lambda props: props.get('file_path', 'Unknown'))
    
    # Group by file and type, then unstack
    complexity_df = df_filtered.groupby(['file_name', 'type']).size().unstack(fill_value=0).reset_index()
    
    # Ensure both columns exist
    if 'Function' not in complexity_df.columns:
        complexity_df['Function'] = 0
    if 'Class' not in complexity_df.columns:
        complexity_df['Class'] = 0
        
    complexity_df = complexity_df.rename(columns={'file_name': 'File', 'Function': 'Functions', 'Class': 'Classes'})
    
    # Sort by total complexity
    complexity_df['Total'] = complexity_df['Functions'] + complexity_df['Classes']
    complexity_df = complexity_df.sort_values(by='Total', ascending=False)
    
    st.dataframe(complexity_df[['File', 'Functions', 'Classes', 'Total']], use_container_width=True)

def show_analytics():
    """Main function to display all analytics on the Streamlit page."""
    
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<p class='medium-font'>📊 Codebase Analytics Dashboard</p>", unsafe_allow_html=True)
    
    output_file = Path("output/parsed_code.json")
    data = read_parse_data(output_file)
    
    if not data or 'nodes' not in data or 'relationships' not in data:
        st.warning("No Python files to display in Project.")
        return
        
    df_nodes = pd.DataFrame(data['nodes'])
    df_relationships = pd.DataFrame(data['relationships'])

    # --- Overview ---
    st.markdown("#### Overview") 
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Files Processed", len(data.get("processed_files", [])))
    col2.metric("Total Nodes", data.get("node_count", 0))
    col3.metric("Total Relationships", data.get("relationship_count", 0))

    # --- Plots ---
    plot_node_distribution(df_nodes)
    plot_relationship_distribution(df_relationships)
    
    # # --- Tables ---
    show_file_complexity(df_nodes) 