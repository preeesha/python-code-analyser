from langchain_ollama import ChatOllama
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
import os

def parse_code_with_llm(file_path="test.py"):
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
            model="gemma3",  
            temperature=0
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

if __name__ == "__main__":
   
    result = parse_code_with_llm("test.py")
    
    display_graph_info(result)
