import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph
from langchain_google_genai import GoogleGenerativeAI
from langchain_neo4j.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_core.prompts import PromptTemplate
from modules.retrival.database import get_schema_from_neo4j

load_dotenv(override=True)

def get_cypher_prompt():
    """Get the configured Cypher prompt template"""
    schema = get_schema_from_neo4j()
    return PromptTemplate.from_template(
        """ 
        You are an expert code graph query generator. Given a natural language question about Python code, generate an accurate Cypher query to retrieve relevant nodes and relationships from the Neo4j database.
        This is the schema of the graph:
        {schema}
        Now generate a Cypher query for in such a way that visualiztion is possible:
        {question}
        Only return the Cypher query. Do not explain anything.
        """
    )

def initialize_graph():
    """Initialize and return Neo4j graph connection"""
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD"),
    )
    graph.refresh_schema()
    return graph

def initialize_llm():
    """Initialize and return the LLM"""
    return GoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL"), 
        temperature=0.1, 
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

def create_query_chain():
    """Create and return the configured GraphCypherQAChain"""
    graph = initialize_graph()
    llm = initialize_llm()
    cypher_prompt = get_cypher_prompt()
    
    chain = GraphCypherQAChain.from_llm(
        llm=llm,
        graph=graph,
        verbose=True,
        return_intermediate_steps=True,
        allow_dangerous_requests=True,
        cypher_prompt=cypher_prompt,
    )
    
    return chain, graph

def process_codebase_query(question):
    """ 
    Returns:
        dict: Dictionary containing 'answer', 'cypher_query', and 'raw_results'
    """
    try:
        chain, graph = create_query_chain()
        response = chain.invoke({"query": question})
        
        # Extract components from response
        answer = response.get('result', 'No answer found')
        cypher_query = response['intermediate_steps'][0]['query'] if response.get('intermediate_steps') else None
        
        # Get raw graph results if available
        raw_results = None
        if cypher_query and not "cannot be answered" in cypher_query.lower():
            try:
                raw_results = graph.query(cypher_query)
            except Exception as e:
                raw_results = f"Error executing query: {str(e)}"
        
        return {
            'answer': answer,
            'cypher_query': cypher_query,
            'raw_results': raw_results,
            'success': True
        }
        
    except Exception as e:
        return {
            'answer': f"Error processing query: {str(e)}",
            'cypher_query': None,
            'raw_results': None,
            'success': False
        }

