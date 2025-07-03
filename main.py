from langchain_ollama import ChatOllama
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
import os
import json
from datetime import datetime

def parse_code_with_llm(file_path="sample_test2.py"):
    """
    Parse Python code from a file using LLMGraphTransformer.
    
    Args:
        file_path (str): Path to the Python file to parse
    
    Returns:
        dict: Parsed graph information with nodes and relationships
    """
    try:
        print("Initializing local Gemma model via Ollama...")
        llm = ChatOllama(
            model="gemma3n:latest",  
            temperature=0.2
        )
        print("✅ Successfully connected to local Gemma model!")
    except Exception as e:
        print(f"❌ Error initializing Gemma model: {e}")
        print("Make sure Ollama is not installed properly")
        return None
    
    # 2. Instantiate transformer
    transformer = LLMGraphTransformer(llm=llm)
    
    # 3. Read code from file
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code_content = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    

    docs = [Document(page_content=code_content, metadata={"source": file_path, "type": "python_code"})]
  
    try:
        graph_docs = transformer.convert_to_graph_documents(docs)
        
        if graph_docs:
            graph = graph_docs[0]
            
            result = {
                "file": file_path,
                "nodes": graph.nodes,
                "relationships": graph.relationships,
                "node_count": len(graph.nodes),
                "relationship_count": len(graph.relationships),
                "parsing_method": "Local Gemma (Ollama)"
            }
            
            return result
        else:
            print("No graph documents generated.")
            return None
            
    except Exception as e:
        print(f"Error during graph transformation: {e}")
        return None

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
    
    print("\n--- NODES ---")
    for i, node in enumerate(graph_info['nodes'], 1):
        print(f"{i}. {node}")
    
    print("\n--- RELATIONSHIPS ---")
    for  relationship in graph_info['relationships']:
        print( relationship)

def save_results_to_json(graph_info, output_file=None):
    """
    Save the parsed graph information to a JSON file.
    
    Args:
        graph_info (dict): Graph information from parse_code_with_llm
        output_file (str): Output file path (optional)
    
    Returns:
        str: Path to the saved JSON file
    """
    if not graph_info:
        print("No graph information to save.")
        return None
    
    # Generate output filename if not provided
    if not output_file:
        output_file = "parsed_code.json"
    
    # Convert complex objects to serializable format
    serializable_data = {
        "file": graph_info['file'],
        "parsing_method": graph_info.get('parsing_method', 'Unknown'),
        "timestamp": datetime.now().isoformat(),
        "node_count": graph_info.get('node_count', 0),
        "relationship_count": graph_info.get('relationship_count', 0),
        "nodes": [],
        "relationships": []
    }
    
    # Convert nodes to dictionaries
    if 'nodes' in graph_info:
        for node in graph_info['nodes']:
            serializable_data['nodes'].append({
                "id": str(node.id) if hasattr(node, 'id') else str(node),
                "type": str(node.type) if hasattr(node, 'type') else "unknown",
                "properties": dict(node.properties) if hasattr(node, 'properties') else {}
            })
    
    # Convert relationships to dictionaries
    if 'relationships' in graph_info:
        for rel in graph_info['relationships']:
            serializable_data['relationships'].append({
                "source": {
                    "id": str(rel.source.id) if hasattr(rel.source, 'id') else str(rel.source),
                    "type": str(rel.source.type) if hasattr(rel.source, 'type') else "unknown"
                },
                "target": {
                    "id": str(rel.target.id) if hasattr(rel.target, 'id') else str(rel.target),
                    "type": str(rel.target.type) if hasattr(rel.target, 'type') else "unknown"
                },
                "relationship_type": str(rel.type) if hasattr(rel, 'type') else "unknown",
                "properties": dict(rel.properties) if hasattr(rel, 'properties') else {}
            })
    
    # Save to JSON file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Results saved to: {output_file}")
        print(f"📊 Saved {len(serializable_data['nodes'])} nodes and {len(serializable_data['relationships'])} relationships")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error saving to JSON: {e}")
        return None

if __name__ == "__main__":
   
    result = parse_code_with_llm("test.py")
    
    # Display the results
    display_graph_info(result)
    
    # Save results to JSON file
    if result:
        json_file = save_results_to_json(result)
        if json_file:
            print(f"🔗 You can view the JSON file: {json_file}")
    else:
        print("❌ No results to save.")
