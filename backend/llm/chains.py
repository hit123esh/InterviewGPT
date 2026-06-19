"""
InterviewGPT — LLM Chains (Utility chains for common LLM operations)
"""

from langchain_core.messages import HumanMessage
from config import get_settings

settings = get_settings()


from llm.agent import get_llm

def get_gemini_llm(temperature: float = 0.7):
    """Get a configured LLM instance."""
    return get_llm()


async def simple_generate(prompt: str, temperature: float = 0.7) -> str:
    """Simple text generation."""
    llm = get_gemini_llm(temperature)
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    return response.content
