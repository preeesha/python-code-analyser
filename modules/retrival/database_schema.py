from langchain_neo4j import Neo4jGraph
from modules.constants.constants import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

def get_schema_from_neo4j():
    graph = Neo4jGraph(
        url=NEO4J_URI,
        username=NEO4J_USER,
        password=NEO4J_PASSWORD,
    )
    return graph.get_schema
