"""
InterviewGPT — Technical Answer Evaluation

Specialized evaluation for technical interview answers.
"""

import json
import logging
from llm.agent import get_llm
from langchain_core.messages import HumanMessage
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def evaluate_technical_answer(
    question: str,
    answer: str,
    context: str = "",
) -> dict:
    """
    Evaluate a technical interview answer.
    
    Returns:
        {
            "score": float,
            "correctness": float,
            "depth": float,
            "accuracy": float,
            "practical_knowledge": float,
            "strengths": [],
            "weaknesses": [],
            "suggestions": []
        }
    """
    llm = get_llm()

    prompt = f"""Evaluate this technical interview answer.

Question: {question}
Answer: {answer}
{f"Context: {context}" if context else ""}

Rate each dimension from 0-10 and return a JSON object:
{{
    "score": <overall score 0-10>,
    "correctness": <technical accuracy 0-10>,
    "depth": <depth of understanding 0-10>,
    "accuracy": <factual accuracy 0-10>,
    "practical_knowledge": <real-world application 0-10>,
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "suggestions": ["suggestion1", "suggestion2"]
}}

Return ONLY the JSON."""

    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(content)
    except Exception as e:
        logger.error(f"Technical evaluation failed: {e}")
        return {"score": 5.0, "strengths": [], "weaknesses": [], "suggestions": []}
