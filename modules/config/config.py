"""
Configuration module for code parsing and graph transformation
Enhanced for CodeGraph AI - Interactive code analysis with semantic relationships
"""

# Enhanced node types for comprehensive code graph analysis
ALLOWED_NODES = [
    "Module",
    "Class",
    "Function",
    "Method",
    "Variable",
    "Constant",
    "Attribute",
]

# Enhanced relationship types for semantic code analysis
ALLOWED_RELATIONSHIPS = [
    "IMPORTS",
    "CONTAINS",
    "CALLS",
    "ACCESSES",
    "DECLARES",
    "USES",
    "RETURNS",
    "INSTANTIATES",
    "PASSES_TO",
    "ASSIGNS",
    
]

# Basic prompt template for LLM
BASIC_PROMPT = """You are a code analysis expert.
Analyze the following Python code and convert it into a graph structure with nodes and relationships. 
Provide the output in JSON format. Be sure to analyze the CURRENT file content, not cached results."""


# Enhanced prompt template for CodeGraph AI
def get_enhanced_prompt(timestamp):
    return f"""You are an expert Python code analyst creating a semantic graph for CodeGraph AI at {timestamp}.

MISSION: Transform Python code into an interactive, queryable knowledge graph that captures:
- Code structure and relationships
- Data flow and dependencies  
- Object-oriented patterns
- Control flow logic
- Import dependencies

IMPORTANT: This is a FRESH analysis. Do NOT use cached results.

REQUIRED NODE PROPERTIES: Give in EXACT SAME FORMAT AS THE EXAMPLE BELOW
For each node, provide rich properties including:
- name: The actual name/identifier
- type: Specific type (function, class, variable, etc.)
- scope: Where it's defined (global, class, function)
- line_number: Where it appears in code
- docstring: If available
- visibility: public, private, protected
- parameters: For functions/methods (name, type, default)
- return_type: For functions/methods
- decorators: List of applied decorators
- base_classes: For class inheritance
- file_path: Source file location

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


# File processing configuration
MAX_CHUNK_SIZE = 8000
LARGE_FILE_THRESHOLD = 15000
CHUNK_OVERLAP_LINES = 10
