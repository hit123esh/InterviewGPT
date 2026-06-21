"""
InterviewGPT — Coding Evaluation
"""

import json
import logging
from backend.llm.agent import get_llm
from langchain_core.messages import HumanMessage
from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def evaluate_code(
    problem: str,
    code: str,
    language: str,
) -> dict:
    """
    Evaluate a coding solution.
    
    Returns:
        {
            "correctness_score": float,
            "efficiency_score": float,
            "time_complexity": str,
            "space_complexity": str,
            "edge_cases_handled": [],
            "edge_cases_missed": [],
            "suggestions": [],
            "improved_solution": str
        }
    """
    llm = get_llm()

    prompt = f"""Evaluate this {language} coding solution.

Problem: {problem}
Code:
```{language}
{code}
```

Return a JSON evaluation:
{{
    "correctness_score": <0-10>,
    "efficiency_score": <0-10>,
    "time_complexity": "<Big O notation>",
    "space_complexity": "<Big O notation>",
    "edge_cases_handled": ["case1", "case2"],
    "edge_cases_missed": ["case1", "case2"],
    "code_quality_notes": ["note1", "note2"],
    "suggestions": ["suggestion1", "suggestion2"],
    "improved_solution": "<improved code if applicable>"
}}

Return ONLY the JSON."""

    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(content)
    except Exception as e:
        logger.error(f"Code evaluation failed: {e}")
        return {"correctness_score": 5.0, "efficiency_score": 5.0, "suggestions": []}
