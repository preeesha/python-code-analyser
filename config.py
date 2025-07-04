"""
Configuration module for code parsing and graph transformation
"""

# Allowed node types for graph transformation
ALLOWED_NODES = [
    "Class",
    "Function",
    "Method",
    "Variable",
    "Parameter",
    "Import",
    "Module",
    "Attribute",
    "Constant",
    "Decorator",
]

# Allowed relationship types for graph transformation
ALLOWED_RELATIONSHIPS = [
    "DEFINES",
    "CONTAINS",
    "CALLS",
    "INHERITS",
    "IMPORTS",
    "USES",
    "ASSIGNS",
    "DECORATES",
    "RETURNS",
    "HAS_PARAMETER",
]

# Prompt template for LLM
BASIC_PROMPT = "You are a code analysis expert. Analyze the following Python code and convert it into a graph structure with nodes and relationships. Provide the output in JSON format. Be sure to analyze the CURRENT file content, not cached results."

# Enhanced prompt template for better results
def get_enhanced_prompt(timestamp):
    return f"""You are a code analysis expert analyzing a Python file at {timestamp}. 
    
    IMPORTANT: This is a FRESH analysis request. Do NOT use any cached results.
    
    Analyze the COMPLETE Python code below and convert it into a graph structure with nodes and relationships. 
    Make sure to identify ALL functions, classes, imports, and variables present in the code.
    Pay special attention to:
    - All function definitions (def function_name)
    - All class definitions  
    - All import statements
    - All variable assignments
    - Function calls and relationships
    
    Process the ENTIRE code content provided:
    {{input}}
    
    Provide comprehensive results based on the COMPLETE code content."""

# File processing configuration
MAX_CHUNK_SIZE = 8000
LARGE_FILE_THRESHOLD = 15000
CHUNK_OVERLAP_LINES = 10 