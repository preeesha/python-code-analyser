from neo4j import GraphDatabase
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Global Neo4j Connection
URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
driver = GraphDatabase.driver(URI, auth=AUTH)  # Now accessible in all functions

def get_data_from_json(file_path):
    file_path = file_path
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def saving_nodes_to_neo4j(file_path="parsed_code.json"):
    # Load fresh data each time
    data = get_data_from_json(file_path)
    nodes = data["nodes"]
    
    for node in nodes:
        try:
            driver.execute_query(
                f"""MERGE (n:Node {{id: '{node['id']}', type: '{node['type']}'}})"""
            )
            print(f"✅ Node {node['id']} created successfully")
        except Exception as e:
            print(f"❌ Error creating node {node['id']}: {e}")

def saving_relationships_to_neo4j(file_path="parsed_code.json"):
    # Load fresh data each time
    data = get_data_from_json(file_path)
    relationships = data["relationships"]
    
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

def deleting_all_nodes_and_relationships():
    with driver.session() as session:
        try:
            session.run("MATCH (n) DETACH DELETE n")
            print("🗑️ All nodes and relationships deleted successfully.")
        except Exception as e:
            print(f"❌ Failed to delete nodes and relationships: {e}")

driver.close()