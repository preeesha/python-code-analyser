#---------------------------------
# Graph transformer module
#---------------------------------
from datetime import datetime

from langchain_core.prompts import PromptTemplate
from langchain_experimental.graph_transformers import LLMGraphTransformer

from modules.llm.prompts import get_enhanced_prompt
from modules.llm.prompts import BASIC_PROMPT

from modules.config.config import ALLOWED_NODES, ALLOWED_RELATIONSHIPS


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
        strict_mode=True,
    )

    return transformer
