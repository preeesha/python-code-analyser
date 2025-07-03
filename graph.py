from neo4j import GraphDatabase
import os
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


nodes=[
    {"id":"Pi","type":"Constant","properties":{}},
    {"id":"Circclearle","type":"Class","properties":{}},
    {"id":"Main","type":"Function","properties":{}},
    {"id":"Datetime","type":"Class","properties":{}},
    {"id":"Math","type":"Module","properties":{}}
]

for node in nodes:
    try:
        driver.execute_query(f"""MERGE (n:Node {{id: '{node['id']}', type: '{node['type']}'}})""")
        print(f"✅ Node {node['id']} created successfully")
    except Exception as e:
        print(f"❌ Error creating node {node['id']}: {e}")

relationships=[
    {"source":{"id":"Circclearle","type":"Class"},"target":{"id":"Main","type":"Function"},"type":"CONTAINS","properties":{}},
    {"source":{"id":"Main","type":"Function"},"target":{"id":"Pi","type":"Constant"},"type":"USES","properties":{}},
    {"source":{"id":"Main","type":"Function"},"target":{"id":"Circclearle","type":"Class"},"type":"CREATES","properties":{}},
    {"source":{"id":"Main","type":"Function"},"target":{"id":"Datetime","type":"Class"},"type":"USES","properties":{}},
    {"source":{"id":"Main","type":"Function"},"target":{"id":"Math","type":"Module"},"type":"USES","properties":{}}
]

for relationship in relationships:
    try:
        driver.execute_query(f"""MATCH(n:Node {{id: '{relationship['source']['id']}'}})
        MATCH(m:Node {{id: '{relationship['target']['id']}'}})
        MERGE (n)-[:{relationship['type']}]->(m)""")
        print(f"✅ Relationship {relationship['type']} created successfully")
    except Exception as e:
        print(f"❌ Error creating relationship {relationship['type']}: {e}")