import time, json
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.documents import Document
from utils import save_json_file  
import os


def parse_code_with_llm(file_path):
    try:
        print("Initializing local Gemma model via Ollama...")
        # llm = ChatOllama(
        #     model="gemma3n",  
        #     temperature=0
        # )
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0 
        )
        print("✅ Successfully connected to gemini model!")
    except Exception as e:
        print(f"❌ Error initializing Gemma model: {e}")
        print("Make sure Ollama is not installed properly")
        return None
    
   
    transformer = LLMGraphTransformer(llm=llm)

    
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
        print("Graph documents generated:", graph_docs)
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



def save_graph_to_file(graph_info, output_dir):
    print(f"Saving graph information to {output_dir}...")
    nodes, relationships = graph_info['nodes'], graph_info['relationships']
    nodes = [node.model_dump() for node in nodes]
    relationships = [relationship.model_dump() for relationship in relationships]

    save_json_file(nodes, os.path.join(output_dir, "nodes.json"))
    save_json_file(relationships, os.path.join(output_dir, "relationships.json"))


def codebaseParserLLM(source_file, output_dir="outputs"):
    print(f"Parsing codebase in {source_file}...")
    result = parse_code_with_llm(source_file) 
    print("Code parsing completed.", result)
    if result:
        display_graph_info(result)
        save_graph_to_file(result, output_dir)
    else:
        print("No valid graph information generated.")


# if __name__ == "__main__":
#     start_time = time.time()
#     print("Starting code parsing and graph generation...")
#     result = parse_code_with_llm("sample/test.py")
#     end_time = time.time()
#     print(f"Parsing completed in {end_time - start_time:.2f} seconds.")
#     display_graph_info(result)
#     save_graph_to_file(result)