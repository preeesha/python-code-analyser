CodeGraph AI 🧠📊
An intelligent system that transforms Python source code into interactive graphs, making complex codebases easy to explore and understand through natural language queries.

🌟 Features

Intelligent Code Analysis: Automatically parses Python source code to extract classes, functions, and variables
Interactive Graph Generation: Creates dynamic decision-flow graphs showing code relationships
Natural Language Queries: Ask questions in plain English about your codebase
Multi-Agent Architecture: Leverages LangGraph with specialized agents for different tasks
Cypher Query Generation: Translates natural language to graph database queries
Rich Visualizations: Returns annotated graphs with insightful explanations
Relationship Mapping: Captures complex relationships between code components

🏗️ Architecture
CodeGraph AI uses a multi-step agentic workflow powered by LangGraph:

┌─────────────────┐    ┌─────────────────┐     ┌─────────────────┐
│   Code Parser   │───▶│ Graph Builder   │───▶│ Query Handler   │
│     Agent       │    │     Agent       │     │     Agent       │
└─────────────────┘    └─────────────────┘     └─────────────────┘
                                                          │
┌─────────────────┐      ┌─────────────────┐              │
│  Visualization  │◀─── | Cypher Generator |◀────────────┘
│     Agent       │      │     Agent       │
└─────────────────┘      └─────────────────┘