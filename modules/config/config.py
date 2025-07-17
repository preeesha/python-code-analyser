
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

# Enhanced prompt template for CodeGraph AI

# File processing configuration
MAX_CHUNK_SIZE = 8000
LARGE_FILE_THRESHOLD = 15000
CHUNK_OVERLAP_LINES = 10
