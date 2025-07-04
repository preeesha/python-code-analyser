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

# def saving_nodes_to_neo4j(file_path="parsed_code.json"):
#     # Load fresh data each time
#     data = get_data_from_json(file_path)
#     nodes = data["nodes"]
    
#     for node in nodes:
#         try:
#             driver.execute_query(
#                 f"""MERGE (n:Node {{id: '{node['id']}', type: '{node['type']}'}})"""
#             )
#             print(f"✅ Node {node['id']} created successfully")
#         except Exception as e:
#             print(f"❌ Error creating node {node['id']}: {e}")


def saving_nodes_to_neo4j(file_path="parsed_code.json"):
    data = get_data_from_json(file_path)
    nodes = data.get("nodes", [])

    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        for node in nodes:
            try:
                label = node["type"]   # Use 'type' as label
                node_id = node["id"]
                props = node.get("properties", {})

                # Add id and type as properties too
                props["id"] = node_id
                props["type"] = label

                # Generate Cypher property string and parameters
                prop_str = ", ".join([f"{k}: ${k}" for k in props])
                cypher = f"MERGE (n:{label} {{id: $id}}) SET n += {{{prop_str}}}"

                driver.execute_query(cypher, props)
                print(f"✅ Node '{node_id}' of type '{label}' created successfully.")
            except Exception as e:
                print(f"❌ Error creating node '{node.get('id', '?')}': {e}")


# def saving_relationships_to_neo4j(file_path="parsed_code.json"):
#     # Load fresh data each time
#     data = get_data_from_json(file_path)
#     relationships = data["relationships"]
    
#     for relationship in relationships:
#         try:
#             driver.execute_query(
#                 f"""MATCH(n:Node {{id: '{relationship['source']['id']}'}})
#                     MATCH(m:Node {{id: '{relationship['target']['id']}'}})
#                     MERGE (n)-[:{relationship['relationship_type']}]->(m)"""
#             )
#             print(f"✅ Relationship {relationship['relationship_type']} created successfully")
#         except Exception as e:
#             print(f"❌ Error creating relationship {relationship['relationship_type']}: {e}")

 
def saving_relationships_to_neo4j(file_path="parsed_code.json"):
    data = get_data_from_json(file_path)
    relationships = data.get("relationships", [])

    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        for rel in relationships:
            try:
                source_id = rel["source"]["id"]
                source_type = rel["source"]["type"]
                target_id = rel["target"]["id"]
                target_type = rel["target"]["type"]
                rel_type = rel["relationship_type"]
                rel_props = rel.get("properties", {})

                # Prepare base Cypher query
                cypher = f"""
                    MATCH (a:{source_type} {{id: $source_id}})
                    MATCH (b:{target_type} {{id: $target_id}})
                    MERGE (a)-[r:{rel_type}]->(b)
                """

                # Only add SET clause if there are properties
                params = {"source_id": source_id, "target_id": target_id}
                if rel_props:
                    rel_prop_str = ", ".join([f"{k}: ${k}" for k in rel_props])
                    cypher += f" SET r += {{{rel_prop_str}}}"
                    params.update(rel_props)

                driver.execute_query(cypher, params)
                print(f"✅ Relationship {rel_type} from {source_id} → {target_id} created successfully")

            except Exception as e:
                print(f"❌ Error creating relationship {rel.get('relationship_type', '?')} from {rel.get('source', {}).get('id', '?')} to {rel.get('target', {}).get('id', '?')}: {e}")


def deleting_all_nodes_and_relationships():
    with driver.session() as session:
        try:
            session.run("MATCH (n) DETACH DELETE n")
            print("🗑️ All nodes and relationships deleted successfully.")
        except Exception as e:
            print(f"❌ Failed to delete nodes and relationships: {e}")

driver.close()