#---------------------------------
# Gemini LLM provider
#---------------------------------
from langchain_google_genai import ChatGoogleGenerativeAI

from modules.constants.constants import (
    GEMINI_MODEL,
    GOOGLE_API_KEY,
)

def initialize_gemini_llm():
    """
    Initialize Google Gemini model

    Returns:
        ChatGoogleGenerativeAI: Initialized Gemini LLM instance
    """
    try:
        print("Initializing Google Gemini model...")
        llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL, google_api_key=GOOGLE_API_KEY, temperature=0
        )
        print("✅ Successfully connected to Google Gemini model!")
        return llm
    except Exception as e:
        print(f"❌ Error initializing Gemini model: {e}")
        return None 