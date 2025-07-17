#---------------------------------
# OpenAI LLM provider
#---------------------------------
from langchain_openai import ChatOpenAI

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
        print("Initializing OpenAI model...")
        llm = ChatOpenAI(
            model=OPENAI_MODEL, openai_api_key=OPENAI_API_KEY, temperature=0
        )
        print("✅ Successfully connected to OpenAI model!")
        return llm
    except Exception as e:
        print(f"❌ Error initializing OpenAI model: {e}")
        return None 