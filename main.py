import os
from neo4j_driver import Neo4jDriver
from parser_agent import codebaseParser
from middleware import convert_ast_to_neo4j_format
from dotenv import load_dotenv
load_dotenv("secrets/.env")


SOURCE_DIR = "sample"
codebaseParser(SOURCE_DIR, OUTPUT_FILE="outputs/project_ast.json")
convert_ast_to_neo4j_format(
    input_file="outputs/project_ast.json", 
    output_nodes_file="outputs/nodes.json", 
    output_relationships_file="outputs/relationships.json"
)
driver = Neo4jDriver(
    uri=os.environ.get("NEO4J_URI"), 
    user=os.environ.get("NEO4J_USER"),
    password=os.environ.get("NEO4J_PASSWORD")
)
driver.load_nodes("outputs/nodes.json")
driver.load_relationships("outputs/relationships.json")








