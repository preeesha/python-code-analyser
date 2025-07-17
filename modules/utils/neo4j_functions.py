from neo4j import GraphDatabase
from modules.constants.constants import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

import json
import os

from modules.config.custom_logger import get_logger

logger = get_logger(__name__)

URI = NEO4J_URI
AUTH = NEO4J_USER, NEO4J_PASSWORD

driver = GraphDatabase.driver(URI, auth=AUTH)


def check_neo4j_connection():
    try:
        with driver.session() as session:
            result = session.run("RETURN 1")
            if result.single()[0] == 1:
                logger.success("Neo4j database connection is active.")
                return True
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
        return False

def get_data_from_json(file_path):
    file_path = file_path
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def saving_nodes_to_neo4j(file_path=os.path.join("outputs", "parsed_code.json")):
    data = get_data_from_json(file_path)
    nodes = data.get("nodes", [])

    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        for node in nodes:
            try:
                label = node["type"]
                node_id = str(node["id"])
                props = node.get("properties", {})

               
                props["id"] = node_id
                props["type"] = label
                if "name" not in props:
                    props["name"] = node_id
                
                prop_str = ", ".join([f"{k}: ${k}" for k in props])
                cypher = f"MERGE (n:{label} {{id: $id}}) SET n += {{{prop_str}}}"

                driver.execute_query(cypher, props)
                logger.success(f"Node '{node_id}' of type '{label}' created successfully.")
            except Exception as e:
                logger.error(f"Error creating node '{node.get('id', '?')}': {e}")


def saving_relationships_to_neo4j(file_path=os.path.join("outputs", "parsed_code.json")):
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

                
                cypher = f"""
                    MATCH (a:{source_type} {{id: $source_id}})
                    MATCH (b:{target_type} {{id: $target_id}})
                    MERGE (a)-[r:{rel_type}]->(b)
                """

                
                params = {"source_id": source_id, "target_id": target_id}
                if rel_props:
                    rel_prop_str = ", ".join([f"{k}: ${k}" for k in rel_props])
                    cypher += f" SET r += {{{rel_prop_str}}}"
                    params.update(rel_props)

                driver.execute_query(cypher, params)
                logger.success(
                    f"Relationship {rel_type} from {source_id} → {target_id} created successfully"
                )

            except Exception as e:
                logger.error(
                    f"Error creating relationship {rel.get('relationship_type', '?')} from {rel.get('source', {}).get('id', '?')} to {rel.get('target', {}).get('id', '?')}: {e}"
                )


def deleting_all_nodes_and_relationships():
    with driver.session() as session:
        try:
            session.run("MATCH (n) DETACH DELETE n")
            logger.success("All nodes and relationships deleted successfully.")
        except Exception as e:
            logger.error(f"Failed to delete nodes and relationships: {e}")


def close_driver():
    """Close the Neo4j driver connection"""
    driver.close()
    logger.success("Neo4j driver connection closed")

