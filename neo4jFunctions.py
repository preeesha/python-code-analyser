from neo4j import GraphDatabase
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Global Neo4j Connection
URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
driver = GraphDatabase.driver(URI, auth=AUTH)  # Now accessible in all functions

def getDataFromJson():
    file_path = "parsed_code.json"
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

data = getDataFromJson()
nodes = data["nodes"]
relationships = data["relationships"]

def savingNodesToNeo4j(nodes):
    for node in nodes:
        try:
            driver.execute_query(
                f"""MERGE (n:Node {{id: '{node['id']}', type: '{node['type']}'}})"""
            )
            print(f"✅ Node {node['id']} created successfully")
        except Exception as e:
            print(f"❌ Error creating node {node['id']}: {e}")

def savingRelationshipsToNeo4j(relationships):
    for relationship in relationships:
        try:
            driver.execute_query(
                f"""MATCH(n:Node {{id: '{relationship['source']['id']}'}})
                    MATCH(m:Node {{id: '{relationship['target']['id']}'}})
                    MERGE (n)-[:{relationship['relationship_type']}]->(m)"""
            )
            print(f"✅ Relationship {relationship['relationship_type']} created successfully")
        except Exception as e:
            print(f"❌ Error creating relationship {relationship['relationship_type']}: {e}")

def deletingAllNodesAndRelationships():
    with driver.session() as session:
        try:
            session.run("MATCH (n) DETACH DELETE n")
            print("🗑️ All nodes and relationships deleted successfully.")
        except Exception as e:
            print(f"❌ Failed to delete nodes and relationships: {e}")

driver.close()