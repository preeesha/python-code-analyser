"""
Prompts for ingestion pipeline - Interactive code analysis with semantic relationships
"""
from langchain_core.prompts import PromptTemplate

BASIC_PROMPT = """You are a code analysis expert.
Analyze the following Python code and convert it into a graph structure with nodes and relationships. 
Provide the output in JSON format. Be sure to analyze the CURRENT file content, not cached results."""


def get_enhanced_prompt(timestamp):
    return f"""You are an expert Python code analyst creating a semantic graph for CodeGraph AI at {timestamp}.

    MISSION: Transform Python code into an interactive, queryable knowledge graph that captures:
    - Code structure and relationships
    - Control flow logic
    - Import dependencies

    IMPORTANT: This is a FRESH analysis. Do NOT use cached results.

    REQUIRED NODE PROPERTIES: Give in EXACT SAME FORMAT AS THE EXAMPLE BELOW
    For each node, provide rich properties including:
    - name: The actual name/identifier
    - type: Specific type (function, class, variable, etc.)
    - line_number: Where it appears in code
    - visibility: public, private, protected
    - parameters: For functions/methods (name, type, default)
    - return_type: For functions/methods
    - base_classes: For class inheritance

    REQUIRED RELATIONSHIP PROPERTIES: GIVE IN EXACT SAME FORMAT AS THE EXAMPLE BELOW
    For each relationship, specify:
    - source: Starting node
    - target: Ending node  
    - relationship_type: Semantic relationship type
    - context: How they're related


    ANALYSIS FOCUS:
    1. **Classes**: Capture inheritance, methods, attributes, properties
    2. **Functions/Methods**: Parameters, return types, calls made, decorators
    3. **Variables**: Scope, assignments, usage patterns, type hints
    4. **Imports**: What's imported, from where, how it's used
    5. **Control Flow**: Conditionals, loops, exception handling
    6. **Data Flow**: How data moves through the code
    7. **Dependencies**: What depends on what


    CODE TO ANALYZE:
    {{input}}

    OUTPUT FORMAT: JSON with nodes array and relationships array, each with comprehensive properties for semantic querying.

    Generate a complete semantic graph that enables natural language queries about code structure, dependencies, and behavior."""

def get_cypher_prompt():
    """Get the configured Cypher prompt template"""

    templete = """ 
            You are an expert Cypher query generator for code graphs. Given a question and a fixed graph schema, generate a Cypher query to retrieve nodes and relationships from Neo4j.

            This is the exact schema:
            {schema}

            Follow these rules STRICTLY:
            1. DO NOT rename or replace any property names, node labels, or relationship types from the schema.
            2. DO NOT rename or change the variable names used in MATCH clauses (e.g., if `m` is used, keep using `m`).
            3. DO NOT reformat or simplify the Cypher query. Keep its original structure and field names exactly the same.
            4. Only return the Cypher query. No explanation or comments.

            Now generate the Cypher query to answer:
            {question}
            """
    return PromptTemplate(template=templete, input_variables=["schema", "question"])


