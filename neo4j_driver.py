from neo4j import GraphDatabase
from utils import load_json_file
from pyvis.network import Network
from py2neo import Node, Relationship
from py2neo import Graph

class Neo4jDriver:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.graph = Graph(uri, auth=(user, password))
        self.LABEL_COLOR_MAP = {
            "Class": "red",
            "Function": "green",
            "Variable": "orange",
            "File": "blue",
            "Default": "gray"
        }

    def close(self):
        self.driver.close()

    def execute_query(self, query, **kwargs):
        with self.driver.session() as session:
            return session.run(query, **kwargs)
    
    def execute_query_v2(self, query):
        return self.graph.run(query)
    
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
            label = node["type"]
            properties = node.get("properties", {})
            safe_label = ''.join(c for c in label if c.isalnum() or c == "_")
            try:
                self.driver.execute_query(
                    f"""
                    MERGE (n:{safe_label} {{id: $id}})
                    SET n.type = $type, n += $properties
                    """,
                    id=node_id, type=node_type, properties=properties
                )   
                print(f"✅ Node ({node_type}) created successfully")
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
            source_label = ''.join(c for c in source["type"] if c.isalnum() or c == "_")
            target_label = ''.join(c for c in target["type"] if c.isalnum() or c == "_")
            
            try:
                self.driver.execute_query(
                    f"""
                    MATCH (a:{source_label} {{id: $source_id}})
                    MATCH (b:{target_label} {{id: $target_id}})
                    MERGE (a)-[r:{rel_type}]->(b)
                    SET r += $properties
                    """,
                    source_id=source["id"],
                    target_id=target["id"],
                    properties=properties
                )
                print(f"✅ Relationship '{rel_type}' created successfully")
            except Exception as e:
                print(f"❌ Error creating relationship '{rel_type}': {e}")
    

    def visualize_neo4j_graph(self, query):
        results = self.graph.run(query)
        net = Network(height="600px", width="100%", notebook=False, directed=True)
        seen_nodes = set()

        print("Neo4j response:", results)

        for record in results:
            nodes_in_record = []
            relationships_in_record = []

            for key, value in record.items():
                if isinstance(value, Node):
                    nodes_in_record.append(value)
                elif isinstance(value, Relationship):
                    relationships_in_record.append(value)
                else:
                    # Handle Subgraph or other mixed types if needed
                    print(f"Unknown type for key '{key}': {type(value)}")

            # Add Nodes Safely
            for node in nodes_in_record:
                node_id = node.identity
                node_label_list = list(node.labels)
                node_label = node_label_list[0] if node_label_list else "Default"
                color = self.LABEL_COLOR_MAP.get(node_label, self.LABEL_COLOR_MAP["Default"])

                if node_id not in seen_nodes:
                    net.add_node(node_id, 
                                label=node.get("name") or str(node_id), 
                                title=str(dict(node)),
                                color=color)
                    seen_nodes.add(node_id)

            # Add Edges if relationships exist and at least 2 nodes present
            if relationships_in_record and len(nodes_in_record) >= 2:
                source = nodes_in_record[0].identity
                target = nodes_in_record[1].identity

                for rel in relationships_in_record:
                    net.add_edge(source, target, label=rel.__class__.__name__)

        # Graph Physics Options
        net.set_options("""
        var options = {
            "physics": {
                "enabled": true,
                "stabilization": {
                    "iterations": 150
                }
            }
        }
        """)

        # Save and Read HTML
        content = net.save_graph("outputs/graph.html")
        with open("outputs/graph.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        return html_content