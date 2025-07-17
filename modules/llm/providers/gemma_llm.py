#---------------------------------
# Gemma LLM provider
#---------------------------------
from langchain_ollama import ChatOllama
from modules.config.custom_logger import get_logger

logger=get_logger(__name__)


def initialize_gemma_llm():
    """
    Initialize local Gemma model via Ollama

    Returns:
        ChatOllama: Initialized Gemma LLM instance
    """
    try:
        llm = ChatOllama(
            model="gemma3n:latest",
            temperature=0,
            top_p=0.5,
        )
        logger.success("Successfully connected to local Gemma model!")
        return llm
    except Exception as e:
        logger.error(f"Error initializing Gemma model: {e}")
        logger.error("Make sure Ollama is installed properly")
        return None 