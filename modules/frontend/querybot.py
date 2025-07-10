import streamlit as st
from modules.frontend.nodes_fromdb import get_color_map
from pyvis.network import Network
import hashlib


def show_query_results(results):
    """
    Create a network graph from Neo4j query results
    
    Args:
        results: List of dictionaries from Neo4j query
        
    Returns:
        pyvis Network object
    """
    net = Network(height="500px", width="100%", bgcolor="#1a1a1a", font_color="white", directed=True)
    added_nodes = set()
    added_edges = set()
    
    if not results:
        return net
    
    # Handle different result formats
    for record in results:
        if isinstance(record, dict):
            # Handle import relationships (like your example)
            if 'imported.name' in record:
                # Create source node (the importing module)
                source_id = "main.py"  # or extract from context
                source_name = "main.py"
                source_label = "Module"
                
                # Create target node (the imported item)
                target_name = record.get('imported.name', 'Unknown')
                target_id = str(hash(target_name)) if target_name else str(hash('unknown'))
                target_label = record.get('imported.type', 'Unknown')
                
                # Add source node
                if source_id not in added_nodes:
                    net.add_node(
                        source_id, 
                        label=source_name, 
                        title=f"Type: {source_label}", 
                        color=get_color_map("parsed_code").get(source_label, "#888888")
                    )
                    added_nodes.add(source_id)
                
                # Add target node
                if target_id not in added_nodes:
                    net.add_node(
                        target_id, 
                        label=target_name, 
                        title=f"Type: {target_label}", 
                        color=get_color_map("parsed_code").get(target_label, "#888888")
                    )
                    added_nodes.add(target_id)
                
                # Add edge
                edge_key = f"{source_id}->{target_id}"
                if edge_key not in added_edges:
                    net.add_edge(source_id, target_id, label="IMPORTS", color="#888")
                    added_edges.add(edge_key)
            
            # Handle standard relationship format
            elif all(key in record for key in ['source_id', 'target_id']):
                source_id = str(record['source_id']) if record['source_id'] is not None else str(hash('unknown_source'))
                target_id = str(record['target_id']) if record['target_id'] is not None else str(hash('unknown_target'))
                
                source_name = record.get('source_name', f"Node_{source_id}")
                target_name = record.get('target_name', f"Node_{target_id}")
                source_label = record.get('source_label', 'Unknown')
                target_label = record.get('target_label', 'Unknown')
                relation = record.get('relation', 'RELATED')
                
                # Add source node
                if source_id not in added_nodes:
                    net.add_node(
                        source_id, 
                        label=source_name, 
                        title=f"Type: {source_label}", 
                        color=get_color_map("parsed_code").get(source_label, "#888888")
                    )
                    added_nodes.add(source_id)
                
                # Add target node
                if target_id not in added_nodes:
                    net.add_node(
                        target_id, 
                        label=target_name, 
                        title=f"Type: {target_label}", 
                        color=get_color_map("parsed_code").get(target_label, "#888888")
                    )
                    added_nodes.add(target_id)
                
                # Add edge
                edge_key = f"{source_id}->{target_id}"
                if edge_key not in added_edges:
                    net.add_edge(source_id, target_id, label=relation, color="#888")
                    added_edges.add(edge_key)
            
            # Handle simple node format
            elif 'id' in record or 'name' in record:
                node_id = record.get('id')
                if node_id is None:
                    # Generate a stable ID from name or other fields
                    name = record.get('name', record.get('label', 'Unknown'))
                    node_id = str(hash(name))
                else:
                    node_id = str(node_id)
                
                node_name = record.get('name', record.get('label', f"Node_{node_id}"))
                node_label = record.get('label', record.get('type', 'Unknown'))
                
                if node_id not in added_nodes:
                    net.add_node(
                        node_id, 
                        label=node_name, 
                        title=f"Type: {node_label}", 
                        color=get_color_map("parsed_code").get(node_label, "#888888")
                    )
                    added_nodes.add(node_id)
    
    return net


def safe_get_node_id(node_data, fallback_key='name'):
    """
    Safely extract or generate a node ID
    
    Args:
        node_data: Dictionary containing node information
        fallback_key: Key to use for generating ID if 'id' is not available
        
    Returns:
        String ID that's safe for pyvis
    """
    node_id = node_data.get('id')
    
    if node_id is not None:
        return str(node_id)
    
    # Generate ID from other fields
    fallback_value = node_data.get(fallback_key, 'unknown')
    return str(hash(fallback_value))