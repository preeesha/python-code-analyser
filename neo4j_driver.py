from neo4j import GraphDatabase
from utils import load_json_file

class Neo4jDriver:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def execute_query(self, query, **kwargs):
        with self.driver.session() as session:
            return session.run(query, **kwargs)
    
    def remove_all_nodes(self):
        try:
            self.execute_query("MATCH (n) DETACH DELETE n")
            print("✅ All nodes and relationships removed successfully")
        except Exception as e:
            print(f"❌ Error removing nodes: {e}")

    def load_nodes(self, nodes_json_file):
        nodes = load_json_file(nodes_json_file)
        for node in nodes:
            node_id = node["id"]
            node_type = node["type"]
            properties = node.get("properties", {})

            try:
                self.driver.execute_query(
                    """
                    MERGE (n:Node {id: $id})
                    SET n.type = $type, n += $properties
                    """,
                    id=node_id, type=node_type, properties=properties
                )
                print(f"✅ Node '{node_id}' ({node_type}) created successfully")
            except Exception as e:
                print(f"❌ Error creating node '{node_id}': {e}")

    # Load Relationships into Neo4j
    def load_relationships(self, relationships_json_file):
        relationships = load_json_file(relationships_json_file)
        for rel in relationships:
            source = rel["source"]
            target = rel["target"]
            rel_type = rel["type"]
            properties = rel.get("properties", {})

            try:
                self.driver.execute_query(
                    f"""
                    MATCH (a:Node {{id: $source_id}})
                    MATCH (b:Node {{id: $target_id}})
                    MERGE (a)-[r:{rel_type}]->(b)
                    SET r += $properties
                    """,
                    source_id=source["id"],
                    target_id=target["id"],
                    properties=properties
                )
                print(f"✅ Relationship '{rel_type}' from '{source['id']}' to '{target['id']}' created successfully")
            except Exception as e:
                print(f"❌ Error creating relationship '{rel_type}': {e}")