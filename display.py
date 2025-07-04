"""
Display and formatting utilities module
"""


def display_graph_info(graph_info):
    """
    Display the parsed graph information in a readable format.

    Args:
        graph_info (dict): Graph information from parse_code_with_llm
    """
    if not graph_info:
        print("No graph information to display.")
        return

    print(f"\n=== Code Analysis for {graph_info['file']} ===")
    print(f"Parsing Method: {graph_info.get('parsing_method', 'Unknown')}")
    print(f"Total Nodes: {graph_info['node_count']}")
    print(f"Total Relationships: {graph_info['relationship_count']}")
    
    # Show chunks info if available
    if graph_info.get('chunks_processed', 1) > 1:
        print(f"Chunks Processed: {graph_info['chunks_processed']}")

    print("\n--- NODES ---")
    for i, node in enumerate(graph_info["nodes"], 1):
        print(f"{i}. {node}")

    print("\n--- RELATIONSHIPS ---")
    for relationship in graph_info["relationships"]:
        print(relationship)


def display_parsing_summary(result):
    """
    Display a summary of parsing results
    
    Args:
        result (dict): Parsing result dictionary
    """
    if not result:
        print("❌ No results to display.")
        return
    
    print(f"\n🎯 PARSING SUMMARY")
    print(f"File: {result.get('file', 'Unknown')}")
    print(f"Content Hash: {result.get('content_hash', 'Unknown')}")
    print(f"Method: {result.get('parsing_method', 'Unknown')}")
    
    if result.get('chunks_processed', 1) > 1:
        print(f"Chunks: {result['chunks_processed']}")
    
    print(f"Nodes: {result.get('node_count', 0)}")
    print(f"Relationships: {result.get('relationship_count', 0)}")


def display_file_stats(file_path, file_info):
    """
    Display file statistics
    
    Args:
        file_path (str): Path to the file
        file_info (dict): File information from read_and_analyze_file
    """
    if not file_info:
        print(f"❌ Could not analyze file: {file_path}")
        return
    
    print(f"\n📊 FILE ANALYSIS")
    print(f"Path: {file_path}")
    print(f"Size: {file_info['size']:,} characters")
    print(f"Hash: {file_info['hash']}")
    print(f"Functions: {file_info['function_count']}")
    
    if file_info['function_count'] > 0:
        print(f"Function names: {', '.join(file_info['functions'][:5])}...")


def display_progress_bar(current, total, prefix="Progress"):
    """
    Display a simple progress bar
    
    Args:
        current (int): Current progress
        total (int): Total items
        prefix (str): Prefix text
    """
    if total == 0:
        return
    
    percent = (current / total) * 100
    bar_length = 20
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    
    print(f'\r{prefix}: |{bar}| {current}/{total} ({percent:.1f}%)', end='', flush=True)
    
    if current == total:
        print()  # New line when complete


def display_nodes_summary(nodes):
    """
    Display a summary of parsed nodes
    
    Args:
        nodes (list): List of node objects
    """
    if not nodes:
        print("No nodes found.")
        return
    
    # Count nodes by type
    node_types = {}
    for node in nodes:
        node_type = getattr(node, 'type', 'Unknown')
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    print(f"\n📋 NODE SUMMARY ({len(nodes)} total)")
    for node_type, count in sorted(node_types.items()):
        print(f"  {node_type}: {count}")


def display_relationships_summary(relationships):
    """
    Display a summary of parsed relationships
    
    Args:
        relationships (list): List of relationship objects
    """
    if not relationships:
        print("No relationships found.")
        return
    
    # Count relationships by type
    rel_types = {}
    for rel in relationships:
        rel_type = getattr(rel, 'type', 'Unknown')
        rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
    
    print(f"\n🔗 RELATIONSHIP SUMMARY ({len(relationships)} total)")
    for rel_type, count in sorted(rel_types.items()):
        print(f"  {rel_type}: {count}")


def print_header(title):
    """
    Print a formatted header
    
    Args:
        title (str): Header title
    """
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def print_section(title):
    """
    Print a formatted section header
    
    Args:
        title (str): Section title
    """
    print(f"\n--- {title} ---") 