import os, sys
from neo4j_driver import Neo4jDriver
from parser_agent import codebaseParser
from parser_agent_llm import codebaseParserLLM
from middleware import convert_ast_to_neo4j_format
from dotenv import load_dotenv
import time
load_dotenv("secrets/.env")


SOURCE_DIR = "C:/Users/QSS/Downloads/CodeGraph AI"

start_time = time.time()
if len(sys.argv) > 1 and sys.argv[1] == "llm":
    source_file = "sample/test.py"
    codebaseParserLLM(source_file, output_dir="outputs")
else: 
    codebaseParser(SOURCE_DIR, OUTPUT_FILE="outputs/project_ast.json")
    convert_ast_to_neo4j_format(
        input_file="outputs/project_ast.json", 
        output_nodes_file="outputs/nodes.json", 
        output_relationships_file="outputs/relationships.json"
    )

end_time = time.time()
print(f"Code parsing completed in {end_time - start_time:.2f} seconds")



driver = Neo4jDriver(
    uri=os.environ.get("NEO4J_URI"), 
    user=os.environ.get("NEO4J_USER"),
    password=os.environ.get("NEO4J_PASSWORD")
)

driver.load_nodes("outputs/nodes.json")
driver.load_relationships("outputs/relationships.json")








