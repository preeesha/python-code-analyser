import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph
from langchain_google_genai import GoogleGenerativeAI
from langchain_neo4j.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_core.prompts import PromptTemplate
from database import get_schema_from_neo4j

load_dotenv(override=True)

schema_text = get_schema_from_neo4j()
CYPHER_PROMPT = PromptTemplate.from_template(
    """ 

You are an expert code graph query generator. Given a natural language question about Python code, generate an accurate Cypher query to retrieve relevant nodes and relationships from the Neo4j database.
This is the schema of the graph:
{schema}
Now generate a Cypher query for:
{question}
Only return the Cypher query. Do not explain anything.
"""
)


graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USER"),
    password=os.getenv("NEO4J_PASSWORD"),
)

llm = GoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL"), temperature=0.1, google_api_key=os.getenv("GOOGLE_API_KEY")
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

question = "explain parse_code_with_llm function?"
response = chain.invoke({"query": question})


cypher_query = response['intermediate_steps'][0]['query']
print("Generated Cypher Query:")

if cypher_query.contains("This question cannot be answered by querying the provided graph schema, as it describes Python code elements and their relationships, not definitions or explanations of external concepts like CypherQAChain"):
    print("This question cannot be answered by querying the provided graph schema, as it describes Python code elements and their relationships, not definitions or explanations of external concepts like CypherQAChain")
else:
    graph_results = graph.query(cypher_query)
    print("\nRaw Graph Data:")
    print(graph_results)
