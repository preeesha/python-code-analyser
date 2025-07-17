from langchain_neo4j import Neo4jGraph
from langchain_google_genai import GoogleGenerativeAI
from langchain_neo4j.chains.graph_qa.cypher import GraphCypherQAChain
from modules.retrival.database_schema import get_schema_from_neo4j
from modules.llm.prompts import get_cypher_prompt
from modules.constants.constants import (
    NEO4J_URI,
    NEO4J_USER,
    NEO4J_PASSWORD,
    GEMINI_MODEL,
    GOOGLE_API_KEY,
)


def initialize_graph():
    """Initialize and return Neo4j graph connection"""
    graph = Neo4jGraph(
        url=NEO4J_URI,
        username=NEO4J_USER,
        password=NEO4J_PASSWORD,
    )
    graph.refresh_schema()
    return graph


def initialize_llm():
    """Initialize and return the LLM"""
    return GoogleGenerativeAI (
        model=GEMINI_MODEL,
        temperature=0.1,
        google_api_key=GOOGLE_API_KEY,
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
        schema = get_schema_from_neo4j()
        response = chain.invoke({"query": question, "schema": schema})

        # Extract components from response
        answer = response.get("result", "No answer found")
        cypher_query = (
            response["intermediate_steps"][0]["query"]
            if response.get("intermediate_steps")
            else None
        )

        # Get raw graph results if available
        raw_results = None
        if cypher_query and not "cannot be answered" in cypher_query.lower():
            try:
                raw_results = graph.query(cypher_query)
            except Exception as e:
                raw_results = f"Error executing query: {str(e)}"

        return {
            "answer": answer,
            "cypher_query": cypher_query,
            "raw_results": raw_results,
            "success": True,
        }

    except Exception as e:
        return {
            "answer": f"Error processing query: {str(e)}",
            "cypher_query": None,
            "raw_results": None,
            "success": False,
        }
