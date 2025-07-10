from langchain_neo4j import Neo4jGraph

import os
from dotenv import load_dotenv

load_dotenv(override=True)


def get_schema_from_neo4j():
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD"),
    )
    return graph.get_schema 


