import os
from langchain_neo4j import Neo4jGraph
from langchain.prompts import PromptTemplate
from langchain_neo4j.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI 
# import logging
# logging.basicConfig(level=logging.DEBUG)

cypher_prompt = PromptTemplate.from_template("""
You are an expert Cypher query generator for Neo4j.  
The graph structure is as follows:

- Nodes:
  - File: properties are `id` (unique filename), `path`, `size_bytes`
  - Class: properties are `name`, `full_name`
  - Function: properties are `name`, `full_name`, `scope`, `is_method`
  - Variable: properties are `name`, `full_name`, `scope`

- Relationships:
  - CONTAINS: indicates structural containment
  - IMPORTS: indicates import dependency

Rules:
1. When querying for a specific file, use `id` or `path`, not `name`
2. Always match relationships explicitly, use `OPTIONAL MATCH` when needed
3. Return results using `RETURN a, r, b` format for visualization
4. For simple node listings, use aliases like `v` for variables, `func` for functions, etc.
5. Only output the Cypher query, no explanation

User Request:
{question}

Cypher:
""")


graph = Neo4jGraph(
    url="neo4j://localhost:7687",
    username=os.environ.get("NEO4J_USER"),
    password=os.environ.get("NEO4J_PASSWORD")
)
#llm = ChatOpenAI(temperature=0, model="gpt-4o")  
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",temperature=0)
#llm = ChatOllama(model="gemma3n",  temperature=0)
graph.refresh_schema()
chain = GraphCypherQAChain.from_llm(
    llm, graph=graph, verbose=True, 
    allow_dangerous_requests=True,
    return_intermediate_steps=True,
    cypher_prompt=cypher_prompt
)  