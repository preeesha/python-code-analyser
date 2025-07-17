import os
from datetime import datetime
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_experimental.graph_transformers import LLMGraphTransformer
from dotenv import load_dotenv
from modules.config.config import ALLOWED_NODES, ALLOWED_RELATIONSHIPS
from modules.llm.prompts import get_enhanced_prompt
from modules.llm.prompts import BASIC_PROMPT

load_dotenv(override=True)

def initialize_gemma_llm():
    """
    Initialize local Gemma model via Ollama
    
    Returns:
        ChatOllama: Initialized Gemma LLM instance
    """
    try:
        print("Initializing local Gemma model via Ollama...")
        llm = ChatOllama(
            model="gemma3n:latest", 
            temperature=0,
            top_p=0.5,
        )
        print("✅ Successfully connected to local Gemma model!")
        return llm
    except Exception as e:
        print(f"❌ Error initializing Gemma model: {e}")
        print("Make sure Ollama is installed properly")
        return None


def initialize_gemini_llm():
    try:
        print("Initializing Google Gemini model...")
        llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0
        )
        print("✅ Successfully connected to Google Gemini model!")
        return llm
    except Exception as e:
        print(f"❌ Error initializing Gemini model: {e}")
        return None


def initialize_openai_llm():
    """
    Initialize OpenAI model
    
    Returns:
        ChatOpenAI: Initialized OpenAI LLM instance
    """
    try:
        print("Initializing OpenAI model...")
        llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0
        )
        print("✅ Successfully connected to OpenAI model!")
        return llm
    except Exception as e:
        print(f"❌ Error initializing OpenAI model: {e}")
        return None


def create_graph_transformer(llm, use_enhanced_prompt=True):
    """
    Create LLMGraphTransformer with the specified LLM
    
    Args:
        llm: Initialized LLM instance
        use_enhanced_prompt (bool): Whether to use enhanced prompt template
        
    Returns:
        LLMGraphTransformer: Configured transformer instance
    """
    if use_enhanced_prompt:
        current_time = datetime.now().isoformat()
        enhanced_prompt = get_enhanced_prompt(current_time)
        prompt_template = PromptTemplate.from_template(enhanced_prompt)
    else:
        prompt_template = PromptTemplate.from_template(BASIC_PROMPT)
    
    transformer = LLMGraphTransformer(
        llm=llm,
        prompt=prompt_template,
        allowed_nodes=ALLOWED_NODES,
        allowed_relationships=ALLOWED_RELATIONSHIPS,
        node_properties=True,
        relationship_properties=True,
        strict_mode=False,
    )
    
    return transformer


def get_default_llm_and_transformer():
    """
    Get default LLM and transformer setup
    
    Returns:
        tuple: (llm, transformer) or (None, None) if setup fails
    """
    # Try Gemini first, fallback to Gemma
    llm = initialize_gemini_llm()
    if llm is None:
        llm = initialize_gemma_llm()
    
    if llm is None:
        return None, None
    
    transformer = create_graph_transformer(llm)
    return llm, transformer 
