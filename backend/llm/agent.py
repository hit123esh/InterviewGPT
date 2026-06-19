"""
InterviewGPT — LangGraph Interview Agent

Stateful interview workflow using LangGraph with:
- Resume context retrieval
- Adaptive question generation
- Answer evaluation
- Dynamic difficulty adjustment
- Report generation
"""
from __future__ import annotations


import json
import logging
from typing import TypedDict, Annotated, Optional, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from config import get_settings
from llm.prompts import (
    QUESTION_GENERATOR_PROMPT,
    ANSWER_EVALUATOR_PROMPT,
    REPORT_GENERATOR_PROMPT,
    get_eval_criteria,
    get_company_context,
)
from rag.retriever import get_resume_context_string

logger = logging.getLogger(__name__)
settings = get_settings()


# ──────────────────────────────────────────────
# Agent State
# ──────────────────────────────────────────────

class InterviewState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_id: str
    resume_context: str
    target_role: str
    interview_type: str
    difficulty: str
    company: Optional[str]
    question_count: int
    max_questions: int
    current_score: float
    scores_history: list[float]
    questions_asked: list[dict]
    current_question: str
    is_finished: bool
    final_report: Optional[dict]


import re

class MockResponse:
    def __init__(self, content: str):
        self.content = content
class MockLLM:
    async def ainvoke(self, messages):
        if isinstance(messages, str):
            prompt = messages
        else:
            prompt = messages[0].content if messages else ""
        
        # 1. Question Generator Prompt
        if "generate the next interview" in prompt.lower() or "previous questions asked" in prompt.lower():
            import re
            role_match = re.search(r"Target Role:\s*(.*)", prompt)
            role = role_match.group(1).strip() if role_match else "Software Engineer"
            
            type_match = re.search(r"Interview Type:\s*(.*)", prompt)
            itype = type_match.group(1).strip() if type_match else "Technical"
            
            diff_match = re.search(r"Current Difficulty:\s*(.*)", prompt)
            diff = diff_match.group(1).strip() if diff_match else "Intermediate"
            
            questions = {
                "dsa": "Can you explain how you would design a data structure that supports insert, delete, search, and getRandom in O(1) time complexity?",
                "system_design": "How would you design a rate limiting system for a large-scale API gateway?",
                "hr": "Tell me about a time when you had a conflict with a team member and how you resolved it.",
                "behavioral": "Describe a challenging project you worked on, what was your role, and what results did you achieve?",
                "technical": "What are the differences between SQL and NoSQL databases, and how do you choose between them for a web application?"
            }
            q_text = questions.get(itype.lower(), f"Can you describe your experience with {role} and what tools you prefer for development?")
            return MockResponse(q_text)
            
        # 2. Answer Evaluator Prompt
        elif "evaluate a candidate's answer" in prompt.lower() or "candidate's answer:" in prompt.lower():
            import re
            ans_match = re.search(r"Candidate's Answer:\s*(.*)", prompt, re.DOTALL)
            ans = ans_match.group(1).strip() if ans_match else ""
            
            score = 7.5
            if len(ans) < 15:
                score = 4.0
                strengths = ["Responded to the question"]
                weaknesses = ["Answer was extremely short and lacked depth", "No examples or details provided"]
                suggestions = ["Try to expand on your answers using the STAR method or providing code snippets", "Explain the core concepts and tradeoffs"]
                diff_adj = "easier"
            else:
                strengths = ["Clearly addressed the question prompt", "Demonstrates practical knowledge of the subject"]
                weaknesses = ["Could provide more technical details on trade-offs", "Did not mention scalability implications"]
                suggestions = ["Mention time/space complexity or architectural tradeoffs", "Use specific concrete examples from your past projects"]
                diff_adj = "harder" if len(ans) > 100 else "same"
                score = min(9.5, 6.0 + (len(ans) / 100.0) * 1.5)
                
            eval_json = {
                "score": round(score, 1),
                "strengths": strengths,
                "weaknesses": weaknesses,
                "suggestions": suggestions,
                "follow_up_recommended": True,
                "difficulty_adjustment": diff_adj
            }
            return MockResponse(json.dumps(eval_json))
            
        # 3. Report Generator Prompt
        else:
            report_json = {
                "executive_summary": "Overall, the candidate showed solid fundamentals and responded to all questions. They communicated clearly but could go deeper into engineering tradeoffs.",
                "technical_assessment": {
                    "score": 7.8,
                    "summary": "Demonstrated good comprehension of core technical topics with a few areas for growth in architecture/scaling.",
                    "key_strengths": ["Good understanding of programming concepts", "Clear structural definitions"],
                    "areas_for_improvement": ["System design scaling parameters", "Concurrency models"]
                },
                "behavioral_assessment": {
                    "score": 8.0,
                    "summary": "Good communication style and STAR structure. Answered behavioral questions clearly.",
                    "communication_quality": "Clear, concise, and structured.",
                    "leadership_indicators": ["Collaborative approach", "Ownership mind-set"]
                },
                "project_knowledge": {
                    "score": 8.5,
                    "summary": "Demonstrates excellent clarity and details about past projects.",
                    "depth_of_understanding": "High"
                },
                "communication_skills": {
                    "score": 8.0,
                    "clarity": "Structured and easy to follow.",
                    "confidence": "Good confidence level.",
                    "articulation": "Clear technical explanations."
                },
                "improvement_areas": [
                    {"area": "System design scalability", "recommendation": "Study load balancers, caching layers, and database sharding techniques.", "priority": "high"},
                    {"area": "Tradeoff evaluation", "recommendation": "When asked a question, always discuss the pros and cons of different solutions.", "priority": "medium"}
                ],
                "learning_path": [
                    {"topic": "System Design Fundamentals", "resource_type": "course/book", "description": "Grokking the System Design Interview"},
                    {"topic": "Advanced Database Management", "resource_type": "article", "description": "Designing Data-Intensive Applications"}
                ],
                "overall_grade": "B+"
            }
            return MockResponse(json.dumps(report_json))

class SafeLLM:
    def __init__(self, real_llm, mock_llm):
        self.real_llm = real_llm
        self.mock_llm = mock_llm

    async def ainvoke(self, messages, *args, **kwargs):
        try:
            return await self.real_llm.ainvoke(messages, *args, **kwargs)
        except Exception as e:
            logger.warning(f"⚠️ Primary LLM call failed ({e}). Falling back to Mock LLM.")
            return await self.mock_llm.ainvoke(messages)

import httpx

class OllamaResponse:
    def __init__(self, content: str):
        self.content = content

class OllamaLLM:
    def __init__(self, url: str, model: str):
        self.url = url.rstrip("/")
        self.model = model

    async def ainvoke(self, messages, *args, **kwargs):
        if isinstance(messages, str):
            ollama_messages = [{"role": "user", "content": messages}]
        else:
            ollama_messages = []
            for msg in messages:
                role = "user"
                class_name = msg.__class__.__name__
                if class_name == "AIMessage":
                    role = "assistant"
                elif class_name == "SystemMessage":
                    role = "system"
                ollama_messages.append({"role": role, "content": msg.content})

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.url}/api/chat",
                json={
                    "model": self.model,
                    "messages": ollama_messages,
                    "stream": False
                }
            )
            if response.status_code == 200:
                data = response.json()
                content = data.get("message", {}).get("content", "")
                return OllamaResponse(content)
            else:
                raise Exception(f"Ollama returned status code {response.status_code}: {response.text}")

def get_llm():
    mock = MockLLM()
    
    if settings.USE_OLLAMA:
        logger.info(f"🤖 Running in Local Ollama Mode with model: {settings.OLLAMA_MODEL}")
        real = OllamaLLM(settings.OLLAMA_URL, settings.OLLAMA_MODEL)
        return SafeLLM(real, mock)
        
    logger.warning("⚠️ Running in Mock LLM Mode for local development.")
    return mock



# ──────────────────────────────────────────────
# Agent Nodes
# ──────────────────────────────────────────────

async def resume_retriever_node(state: InterviewState) -> dict:
    """Retrieve relevant resume context for question generation."""
    query = f"{state['interview_type']} interview questions for {state['target_role']}"
    
    if state["questions_asked"]:
        last_q = state["questions_asked"][-1]
        query = last_q.get("question", query)

    context = await get_resume_context_string(
        user_id=state["user_id"],
        query=query,
        n_results=5,
    )
    return {"resume_context": context}


async def question_generator_node(state: InterviewState) -> dict:
    """Generate the next interview question."""
    llm = get_llm()

    previous_questions = "\n".join(
        [f"Q{i+1}: {q['question']}" for i, q in enumerate(state["questions_asked"])]
    ) or "None (this is the first question)"

    previous_answer = ""
    previous_score = "N/A"
    if state["questions_asked"]:
        last = state["questions_asked"][-1]
        previous_answer = last.get("answer", "No answer provided")
        previous_score = str(last.get("score", "N/A"))

    company_context = get_company_context(state.get("company"))

    prompt = QUESTION_GENERATOR_PROMPT.format(
        interview_type=state["interview_type"],
        target_role=state["target_role"],
        difficulty=state["difficulty"],
        company_context=company_context,
        resume_context=state["resume_context"],
        previous_questions=previous_questions,
        previous_answer=previous_answer,
        previous_score=previous_score,
    )

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    question_text = response.content.strip()

    return {
        "current_question": question_text,
        "messages": [AIMessage(content=question_text)],
    }


async def answer_evaluator_node(state: InterviewState) -> dict:
    """Evaluate the candidate's most recent answer."""
    llm = get_llm()

    if not state["questions_asked"]:
        return {}

    last_qa = state["questions_asked"][-1]
    question = last_qa.get("question", "")
    answer = last_qa.get("answer", "")

    if not answer:
        return {}

    eval_criteria = get_eval_criteria(state["interview_type"])
    company_context = get_company_context(state.get("company"))

    prompt = ANSWER_EVALUATOR_PROMPT.format(
        interview_type=state["interview_type"],
        target_role=state["target_role"],
        question=question,
        answer=answer,
        evaluation_criteria=eval_criteria,
    )

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    content = response.content.strip()

    # Parse JSON response
    try:
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0]
        evaluation = json.loads(content)
    except (json.JSONDecodeError, IndexError):
        evaluation = {
            "score": 5.0,
            "strengths": ["Answer provided"],
            "weaknesses": ["Could not fully evaluate"],
            "suggestions": ["Try to be more specific"],
            "follow_up_recommended": False,
            "difficulty_adjustment": "same",
        }

    score = float(evaluation.get("score", 5.0))
    new_scores = state["scores_history"] + [score]
    avg_score = sum(new_scores) / len(new_scores)

    # Update the last question with evaluation
    updated_questions = state["questions_asked"].copy()
    updated_questions[-1]["evaluation"] = evaluation
    updated_questions[-1]["score"] = score

    return {
        "scores_history": new_scores,
        "current_score": avg_score,
        "questions_asked": updated_questions,
    }


async def difficulty_adjuster_node(state: InterviewState) -> dict:
    """Adjust difficulty based on running score average."""
    avg_score = state["current_score"]

    if avg_score >= 8:
        new_difficulty = "advanced"
    elif avg_score >= 5:
        new_difficulty = "intermediate"
    else:
        new_difficulty = "beginner"

    return {"difficulty": new_difficulty}


async def report_generator_node(state: InterviewState) -> dict:
    """Generate the final interview report."""
    llm = get_llm()

    qa_summary = ""
    for i, qa in enumerate(state["questions_asked"]):
        qa_summary += f"\nQ{i+1}: {qa.get('question', 'N/A')}\n"
        qa_summary += f"A{i+1}: {qa.get('answer', 'No answer')}\n"
        evaluation = qa.get("evaluation", {})
        qa_summary += f"Score: {qa.get('score', 'N/A')}/10\n"
        qa_summary += f"Strengths: {', '.join(evaluation.get('strengths', []))}\n"
        qa_summary += f"Weaknesses: {', '.join(evaluation.get('weaknesses', []))}\n"

    company_context = get_company_context(state.get("company"))

    prompt = REPORT_GENERATOR_PROMPT.format(
        interview_type=state["interview_type"],
        target_role=state["target_role"],
        difficulty=state["difficulty"],
        company_context=company_context,
        qa_summary=qa_summary,
        overall_score=f"{state['current_score']:.1f}",
    )

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    content = response.content.strip()

    try:
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0]
        report = json.loads(content)
    except (json.JSONDecodeError, IndexError):
        report = {
            "executive_summary": "Interview completed. Please review individual question scores.",
            "overall_grade": _score_to_grade(state["current_score"]),
        }

    return {
        "final_report": report,
        "is_finished": True,
    }


# ──────────────────────────────────────────────
# Routing Logic
# ──────────────────────────────────────────────

def should_continue(state: InterviewState) -> str:
    """Decide whether to continue interviewing or generate report."""
    if state.get("is_finished"):
        return "end"
    if state["question_count"] >= state["max_questions"]:
        return "generate_report"
    return "retrieve_context"


def after_evaluation(state: InterviewState) -> str:
    """After evaluating, decide next step."""
    if state["question_count"] >= state["max_questions"]:
        return "generate_report"
    return "adjust_difficulty"


# ──────────────────────────────────────────────
# Graph Builder
# ──────────────────────────────────────────────

def build_interview_graph() -> StateGraph:
    """Build the LangGraph interview workflow."""
    workflow = StateGraph(InterviewState)

    # Add nodes
    workflow.add_node("retrieve_context", resume_retriever_node)
    workflow.add_node("generate_question", question_generator_node)
    workflow.add_node("evaluate_answer", answer_evaluator_node)
    workflow.add_node("adjust_difficulty", difficulty_adjuster_node)
    workflow.add_node("generate_report", report_generator_node)

    # Set entry point
    workflow.set_entry_point("retrieve_context")

    # Add edges
    workflow.add_edge("retrieve_context", "generate_question")
    # After question generation, we return to the API (wait for answer)
    # The "evaluate_answer" node is called when an answer comes in
    workflow.add_conditional_edges(
        "evaluate_answer",
        after_evaluation,
        {
            "adjust_difficulty": "adjust_difficulty",
            "generate_report": "generate_report",
        }
    )
    workflow.add_edge("adjust_difficulty", "retrieve_context")
    workflow.add_edge("generate_report", END)

    return workflow


# Compile the graph
interview_graph = build_interview_graph()
compiled_graph = interview_graph.compile()


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

async def start_interview(
    user_id: str,
    target_role: str,
    interview_type: str,
    difficulty: str,
    max_questions: int,
    company: str | None = None,
) -> dict:
    """Initialize and start an interview, returning the first question."""
    initial_state: InterviewState = {
        "messages": [],
        "user_id": user_id,
        "resume_context": "",
        "target_role": target_role,
        "interview_type": interview_type,
        "difficulty": difficulty,
        "company": company,
        "question_count": 0,
        "max_questions": max_questions,
        "current_score": 0.0,
        "scores_history": [],
        "questions_asked": [],
        "current_question": "",
        "is_finished": False,
        "final_report": None,
    }

    # Run through retrieve_context → generate_question
    # We invoke just the first two nodes
    state = initial_state.copy()
    
    # Retrieve context
    ctx_update = await resume_retriever_node(state)
    state.update(ctx_update)
    
    # Generate first question
    q_update = await question_generator_node(state)
    state.update(q_update)
    state["question_count"] = 1
    state["questions_asked"] = [{
        "question": state["current_question"],
        "question_number": 1,
        "difficulty": state["difficulty"],
    }]

    return {
        "question": state["current_question"],
        "question_number": 1,
        "difficulty": state["difficulty"],
        "agent_state": _serialize_state(state),
    }


async def submit_answer(agent_state: dict, answer: str) -> dict:
    """
    Process a candidate's answer:
    1. Evaluate the answer
    2. Adjust difficulty
    3. Generate next question (or report if done)
    """
    state = _deserialize_state(agent_state)

    # Record the answer
    if state["questions_asked"]:
        state["questions_asked"][-1]["answer"] = answer
    state["messages"].append(HumanMessage(content=answer))

    # Evaluate
    eval_update = await answer_evaluator_node(state)
    state.update(eval_update)

    # Check if we should finish
    if state["question_count"] >= state["max_questions"]:
        report_update = await report_generator_node(state)
        state.update(report_update)
        return {
            "is_finished": True,
            "evaluation": state["questions_asked"][-1].get("evaluation", {}),
            "final_report": state["final_report"],
            "overall_score": state["current_score"],
            "agent_state": _serialize_state(state),
        }

    # Adjust difficulty
    diff_update = await difficulty_adjuster_node(state)
    state.update(diff_update)

    # Retrieve new context and generate next question
    ctx_update = await resume_retriever_node(state)
    state.update(ctx_update)
    
    q_update = await question_generator_node(state)
    state.update(q_update)
    state["question_count"] += 1
    state["questions_asked"].append({
        "question": state["current_question"],
        "question_number": state["question_count"],
        "difficulty": state["difficulty"],
    })

    return {
        "is_finished": False,
        "question": state["current_question"],
        "question_number": state["question_count"],
        "difficulty": state["difficulty"],
        "evaluation": state["questions_asked"][-2].get("evaluation", {}),
        "current_score": state["current_score"],
        "agent_state": _serialize_state(state),
    }


async def end_interview_early(agent_state: dict) -> dict:
    """End interview early and generate report."""
    state = _deserialize_state(agent_state)
    
    if state["scores_history"]:
        report_update = await report_generator_node(state)
        state.update(report_update)
    
    return {
        "final_report": state.get("final_report"),
        "overall_score": state["current_score"],
        "questions_answered": len([q for q in state["questions_asked"] if q.get("answer")]),
        "agent_state": _serialize_state(state),
    }


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _serialize_state(state: InterviewState) -> dict:
    """Serialize state for JSON storage."""
    serialized = {}
    for key, value in state.items():
        if key == "messages":
            serialized[key] = [
                {"type": type(m).__name__, "content": m.content}
                for m in value
            ]
        else:
            serialized[key] = value
    return serialized


def _deserialize_state(data: dict) -> InterviewState:
    """Deserialize state from JSON storage."""
    state = data.copy()
    messages = []
    for msg in data.get("messages", []):
        if msg["type"] == "HumanMessage":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["type"] == "AIMessage":
            messages.append(AIMessage(content=msg["content"]))
        elif msg["type"] == "SystemMessage":
            messages.append(SystemMessage(content=msg["content"]))
    state["messages"] = messages
    return state


def _score_to_grade(score: float) -> str:
    if score >= 9.5: return "A+"
    if score >= 8.5: return "A"
    if score >= 7.5: return "B+"
    if score >= 6.5: return "B"
    if score >= 5.5: return "C+"
    if score >= 4.5: return "C"
    if score >= 3.0: return "D"
    return "F"


def calculate_max_questions(duration_minutes: int) -> int:
    """Calculate max questions based on interview duration."""
    # Roughly 3-4 minutes per question including evaluation
    return max(3, duration_minutes // 4)
