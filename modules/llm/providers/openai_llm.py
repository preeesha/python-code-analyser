#---------------------------------
# OpenAI LLM provider
#---------------------------------
from langchain_openai import ChatOpenAI

from modules.config.custom_logger import get_logger

logger=get_logger(__name__)

from modules.constants.constants import (
    OPENAI_MODEL,
    OPENAI_API_KEY,
)


def initialize_openai_llm():
    """
    Initialize OpenAI model

    Returns:
        ChatOpenAI: Initialized OpenAI LLM instance
    """
    try:
        logger.info("Initializing OpenAI model...")
        llm = ChatOpenAI(
            model=OPENAI_MODEL, openai_api_key=OPENAI_API_KEY, temperature=0
        )
        logger.success("Successfully connected to OpenAI model!")
        return llm
    except Exception as e:
        logger.error(f"Error initializing OpenAI model: {e}")
        return None 