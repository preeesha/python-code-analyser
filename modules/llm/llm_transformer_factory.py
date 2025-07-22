#---------------------------------
# LLM setup module
#---------------------------------

from modules.llm.graph_transformer import create_graph_transformer

from modules.llm.providers.gemma_llm import initialize_gemma_llm
from modules.llm.providers.gemini_llm import initialize_gemini_llm
from modules.llm.providers.openai_llm import initialize_openai_llm


def llm_transformer_factory():
    """
    Get default LLM and transformer setup

    Returns:
        tuple: (llm, transformer) or (None, None) if setup fails
    """
    llm = initialize_gemini_llm()

    if llm is None:
        return None, None

    transformer = create_graph_transformer(llm)
    return llm, transformer
