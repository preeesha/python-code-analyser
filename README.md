# Python Code Analyzer 🐍

A sophisticated codebase analysis and visualization tool that leverages Large Language Models (LLMs) and graph databases to provide deep insights into Python codebases. Transform your code into an interactive knowledge graph and query it using natural language.

## 🚀 Features

### Core Capabilities
- **Intelligent Code Analysis**: Uses LLMs to understand code structure, relationships, and dependencies
- **Graph Database Storage**: Stores code relationships in Neo4j for efficient querying and visualization
- **Multi-Provider LLM Support**: Compatible with OpenAI, Google Gemini, and Gemma (via Ollama)
- **Interactive Visualization**: Generate network graphs to visualize codebase architecture
- **Natural Language Querying**: Ask questions about your codebase using a conversational AI interface

### Input Methods
- **ZIP File Upload**: Analyze compressed codebases
- **GitHub Repository**: Direct integration with GitHub repositories
- **Local Directory**: Process local project directories

### Dashboard Pages
- **Analytics Dashboard**: Comprehensive metrics and insights about your codebase
- **Codebase Visualizer**: Interactive network graphs showing code relationships
- **Query Bot**: Natural language interface for codebase exploration

## 🏗️ Architecture

The project follows a modular, clean architecture pattern:

```
├── modules/
│   ├── config/          # Configuration and logging setup
│   ├── constants/       # Application constants
│   ├── frontend/        # Streamlit UI components
│   ├── llm/            # Language model integrations and transformers
│   ├── retrieval/      # Database schema and query processing
│   └── utils/          # Utility functions and helpers
├── pages/              # Streamlit pages
└── outputs/            # Generated analysis results
```

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Graph Database**: Neo4j
- **LLM Framework**: LangChain
- **Visualization**: Pyvis, NetworkX, Plotly
- **Data Processing**: Pandas
- **Environment Management**: Python-dotenv

## 📋 Prerequisites

- Python 3.8+
- Neo4j Database (local or cloud instance)
- API keys for your chosen LLM provider(s):
  - OpenAI API key (optional)
  - Google Gemini API key (optional)
  - Ollama for local Gemma models (optional)

## ⚙️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd python-code-analyzer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Neo4j**:
   - Install Neo4j Desktop or use Neo4j Cloud
   - Create a new database instance
   - Note the connection details (URI, username, password)

4. **Configure environment variables**:
   rename `.env.sample` file present in the project root and add required information.
    

## 🚀 Usage

1. **Start the application**:
   ```bash
   streamlit run Main.py
   ```

2. **Upload your codebase**:
   - Choose your preferred input method (ZIP, GitHub, or local directory)
   - Configure analysis parameters
   - Select your LLM provider

3. **Analyze your code**:
   - The system will process your codebase using the ingestion pipeline
   - Code relationships will be extracted and stored in Neo4j
   - Analysis results will be available across all dashboard pages

4. **Explore insights**:
   - **Analytics Dashboard**: View codebase metrics and statistics
   - **Codebase Visualizer**: Interact with the knowledge graph
   - **Query Bot**: Ask natural language questions about your code

## Key Data Flow Points:

#### Ingestion Pipeline:
1. **Input Processing**: ZIP/GitHub/Local files → `testing/` directory
2. **File Parsing**: Python files → LLM analysis → Graph documents
3. **Data Transformation**: Code → Nodes & Relationships → JSON
4. **Storage**: JSON → Neo4j database
5. **Cleanup**: Clear temporary files

#### Query Pipeline:
1. **Query Input**: Natural language → LLM processing
2. **Schema Retrieval**: Neo4j → Database schema
3. **Query Generation**: LLM → Cypher query
4. **Execution**: Cypher → Neo4j → Raw results
5. **Visualization**: Results → PyVis network → Streamlit display

## 🆘 Support

For issues and questions:
- Check the logs in the application interface
- Verify Neo4j connection settings
- Ensure LLM API keys are correctly configured
- Review the ingestion pipeline logs for processing errors 