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
    
    def add_node_from_data(node_data, added_nodes, net):
        """Helper function to add a node to the network"""
        node_id = node_data.get('id', str(hash(node_data.get('name', 'unknown'))))
        node_name = node_data.get('name', f"Node_{node_id}")
        node_type = node_data.get('type', 'Unknown')
        
        # Create detailed title with additional info
        title = f"Type: {node_type}"
        if 'file_path' in node_data and node_data['file_path']:
            title += f"<br/>File: {node_data['file_path']}"
        if 'scope' in node_data and node_data['scope']:
            title += f"<br/>Scope: {node_data['scope']}"
        if 'line_number' in node_data and node_data['line_number']:
            title += f"<br/>Line: {node_data['line_number']}"
        if 'visibility' in node_data and node_data['visibility']:
            title += f"<br/>Visibility: {node_data['visibility']}"
        
        if node_id not in added_nodes:
            net.add_node(
                node_id, 
                label=node_name, 
                title=title, 
                color=get_color_map("parsed_code").get(node_type, "#888888")
            )
            added_nodes.add(node_id)
        
        return node_id
    
    def add_relationship(source_node, target_node, relationship_type, added_nodes, added_edges, net):
        """Helper function to add a relationship between two nodes"""
        source_id = add_node_from_data(source_node, added_nodes, net)
        target_id = add_node_from_data(target_node, added_nodes, net)
        
        # Add edge with unique identifier to handle multiple relationships between same nodes
        edge_key = f"{source_id}->{target_id}-{relationship_type}"
        if edge_key not in added_edges:
            net.add_edge(source_id, target_id, label=relationship_type, color="#888")
            added_edges.add(edge_key)
    
    # Handle different result formats
    for record in results:
        if isinstance(record, dict):
            # Handle complex Neo4j relationship format with multiple relationships per record
            relationships_handled = False
            
            # Process 'r' relationship if exists
            if 'r' in record and isinstance(record['r'], tuple) and len(record['r']) == 3:
                source_node, relationship_type, target_node = record['r']
                add_relationship(source_node, target_node, relationship_type, added_nodes, added_edges, net)
                relationships_handled = True
            
            # Process 's' relationship if exists  
            if 's' in record and isinstance(record['s'], tuple) and len(record['s']) == 3:
                source_node, relationship_type, target_node = record['s']
                add_relationship(source_node, target_node, relationship_type, added_nodes, added_edges, net)
                relationships_handled = True
            
            # Also handle individual nodes from 'f', 'source', 'target' if they exist and no relationships were processed
            if not relationships_handled:
                # Handle alternative format with separate 'source' and 'target' keys
                if 'source' in record and 'target' in record:
                    source_node = record['source']
                    target_node = record['target']
                    
                    # Extract relationship type from 'r' if available
                    relationship_type = "RELATED"
                    if 'r' in record and isinstance(record['r'], tuple) and len(record['r']) >= 2:
                        relationship_type = record['r'][1]
                    
                    add_relationship(source_node, target_node, relationship_type, added_nodes, added_edges, net)
                
                # Handle import relationships
                elif 'imported.name' in record:
                    # Create source node (the importing module)
                    source_node = {'id': 'main.py', 'name': 'main.py', 'type': 'Module'}
                    
                    # Create target node (the imported item)
                    target_name = record.get('imported.name', 'Unknown')
                    target_node = {
                        'id': str(hash(target_name)) if target_name else str(hash('unknown')),
                        'name': target_name,
                        'type': record.get('imported.type', 'Unknown')
                    }
                    
                    add_relationship(source_node, target_node, "IMPORTS", added_nodes, added_edges, net)
                
                # Handle standard relationship format
                elif all(key in record for key in ['source_id', 'target_id']):
                    source_node = {
                        'id': str(record['source_id']) if record['source_id'] is not None else str(hash('unknown_source')),
                        'name': record.get('source_name', f"Node_{record['source_id']}"),
                        'type': record.get('source_label', 'Unknown')
                    }
                    
                    target_node = {
                        'id': str(record['target_id']) if record['target_id'] is not None else str(hash('unknown_target')),
                        'name': record.get('target_name', f"Node_{record['target_id']}"),
                        'type': record.get('target_label', 'Unknown')
                    }
                    
                    relation = record.get('relation', 'RELATED')
                    add_relationship(source_node, target_node, relation, added_nodes, added_edges, net)
                
                # Handle simple node format (single nodes without relationships)
                elif 'id' in record or 'name' in record:
                    add_node_from_data(record, added_nodes, net)
                
                # Handle individual function node from 'f' key
                elif 'f' in record:
                    add_node_from_data(record['f'], added_nodes, net)
    
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