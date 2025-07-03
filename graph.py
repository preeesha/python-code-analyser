from neo4j import GraphDatabase
import os
import json
from dotenv import load_dotenv
load_dotenv()

URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    try:
        driver.verify_connectivity()
        print("✅ Connected to Neo4j successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

file_path="parsed_code.json"
with open(file_path, 'r') as file:
    data = json.load(file)

nodes=data["nodes"]
relationships=data["relationships"]



for node in nodes:
    try:
        driver.execute_query(f"""MERGE (n:Node {{id: '{node['id']}', type: '{node['type']}'}})""")
        print(f"✅ Node {node['id']} created successfully")
    except Exception as e:
        print(f"❌ Error creating node {node['id']}: {e}")
        


for relationship in relationships:
    try:
        driver.execute_query(f"""MATCH(n:Node {{id: '{relationship['source']['id']}'}})
        MATCH(m:Node {{id: '{relationship['target']['id']}'}})
        MERGE (n)-[:{relationship['relationship_type']}]->(m)""")
        print(f"✅ Relationship {relationship['relationship_type']} created successfully")
    except Exception as e:
        print(f"❌ Error creating relationship {relationship['relationship_type']}: {e}")
        
# with driver.session() as session:
#     try:
#         session.run("MATCH (n) DETACH DELETE n")
#         print("🗑️ All nodes and relationships deleted successfully.")
#     except Exception as e:
#         print(f"❌ Failed to delete nodes and relationships: {e}")
