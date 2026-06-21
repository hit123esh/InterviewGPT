"""
InterviewGPT — Behavioral Answer Evaluation (STAR Method)
"""

import json
import logging
from langchain_core.messages import HumanMessage
from backend.config import get_settings
from backend.llm.agent import get_llm

logger = logging.getLogger(__name__)
settings = get_settings()


async def evaluate_behavioral_answer(
    question: str,
    answer: str,
) -> dict:
    """
    Evaluate a behavioral interview answer using STAR methodology.
    
    Returns:
        {
            "score": float,
            "star_analysis": {
                "situation": { "present": bool, "quality": float },
                "task": { "present": bool, "quality": float },
                "action": { "present": bool, "quality": float },
                "result": { "present": bool, "quality": float }
            },
            "completeness": float,
            "confidence": float,
            "specificity": float,
            "leadership_indicators": [],
            "strengths": [],
            "weaknesses": [],
            "suggestions": []
        }
    """
    llm = get_llm()


    prompt = f"""Evaluate this behavioral interview answer using the STAR method.

Question: {question}
Answer: {answer}

Analyze the answer for STAR structure and return a JSON object:
{{
    "score": <overall score 0-10>,
    "star_analysis": {{
        "situation": {{ "present": <bool>, "quality": <0-10> }},
        "task": {{ "present": <bool>, "quality": <0-10> }},
        "action": {{ "present": <bool>, "quality": <0-10> }},
        "result": {{ "present": <bool>, "quality": <0-10> }}
    }},
    "completeness": <0-10>,
    "confidence": <0-10>,
    "specificity": <0-10>,
    "leadership_indicators": ["indicator1", "indicator2"],
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
        logger.error(f"Behavioral evaluation failed: {e}")
        return {"score": 5.0, "strengths": [], "weaknesses": [], "suggestions": []}
