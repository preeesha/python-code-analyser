import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph
from langchain_google_genai import GoogleGenerativeAI
from langchain_neo4j.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_core.prompts import PromptTemplate


load_dotenv(override=True)

CYPHER_PROMPT = PromptTemplate.from_template(
    """ 

You are an expert code graph query generator. Given a natural language question about Python code, generate an accurate Cypher query to retrieve relevant nodes and relationships from the Neo4j database.

The graph is structured with:

1. **Nodes** with labels like `Function`, `Class`, `Method`, `Module`, `Variable`, `Attribute`, `Constant` — each having properties such as:
   - `name`, `type`, `scope`, `line_number`, `docstring`, `visibility`, `parameters`, `return_type`, `decorators`, `base_classes`, `file_path`

2. **Relationships** such as `ACCESSES`, `ASSIGNS`, `CALLS`, `CONTAINS`, `DECLARES`, `IMPORTS`, `INSTANTIATES`, `PASSES_TO`, `RETURNS`, `USES`, each possibly having properties:
   - `relationship_type`, `context`, `line_number`, `description`

Important Guidelines:
- Generate **precise Cypher queries** that match node labels and property names **exactly** as described.
- If the question is ambiguous, generate the **best guess** query that could retrieve relevant info.
- If no specific file is mentioned, search across the entire codebase.
- Only return the **Cypher query** — do not explain it.
- Use aliasing for readability (e.g., `MATCH (f:Function)-[:CALLS]->(c:Class) RETURN f.name, c.name`)
- Always **limit results** to 10 unless explicitly asked for more.

Now generate a Cypher query for:
{query}
"""
)


graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USER"),
    password=os.getenv("NEO4J_PASSWORD"),
)

llm = GoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL"), temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY")
)

chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    return_intermediate_steps=True,
    allow_dangerous_requests=True,
    cypher_prompt=CYPHER_PROMPT,
)
graph.refresh_schema()

question = "explain Neo4j_functions?"
response = chain.invoke({"query": question})

print(response)
