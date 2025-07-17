#---------------------------------
# Gemma LLM provider
#---------------------------------
from langchain_ollama import ChatOllama


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