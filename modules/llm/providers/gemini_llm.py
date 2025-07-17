#---------------------------------
# Gemini LLM provider
#---------------------------------
from modules.config.custom_logger import get_logger

from langchain_google_genai import ChatGoogleGenerativeAI

from modules.constants.constants import (
    GEMINI_MODEL,
    GOOGLE_API_KEY,
)

logger=get_logger(__name__)

def initialize_gemini_llm():
    """
    Initialize Google Gemini model

    Returns:
        ChatGoogleGenerativeAI: Initialized Gemini LLM instance
    """
    try:
        logger.info("Initializing Google Gemini model...")
        llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL, google_api_key=GOOGLE_API_KEY, temperature=0
        )
        logger.success("Successfully connected to Google Gemini model!")
        return llm
    
    except Exception as e:
        logger.error(f" Error initializing Gemini model: {e}")
        return None 