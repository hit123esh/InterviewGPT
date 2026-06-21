"""
InterviewGPT — Interview API Router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from backend.database import get_db
from backend.database.models import User
from backend.auth.dependencies import get_current_user
from backend.interviews.schemas import (
    InterviewCreate, InterviewResponse, InterviewListResponse,
    AnswerSubmit, QuestionResponse, InterviewQuestionResponse,
)
from backend.interviews.service import (
    create_interview, start_interview_session, process_answer,
    end_interview, get_user_interviews, get_interview_by_id,
    get_interview_questions,
)

router = APIRouter(prefix="/interviews", tags=["Interviews"])


@router.post("/create", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_new_interview(
    data: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new interview session."""
    # Validate interview type
    valid_types = ["hr", "technical", "dsa", "system_design", "project_discussion"]
    if data.interview_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid interview type. Must be one of: {valid_types}",
        )

    valid_difficulties = ["beginner", "intermediate", "advanced"]
    if data.difficulty not in valid_difficulties:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid difficulty. Must be one of: {valid_difficulties}",
        )

    interview = await create_interview(db, current_user.id, data)
    return interview


@router.get("/", response_model=InterviewListResponse)
async def list_interviews(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all interviews for the current user."""
    interviews = await get_user_interviews(db, current_user.id, skip, limit)
    return InterviewListResponse(interviews=interviews, total=len(interviews))


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get interview details."""
    interview = await get_interview_by_id(db, interview_id, current_user.id)
    if not interview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")
    return interview


@router.post("/{interview_id}/start", response_model=QuestionResponse)
async def start_interview(
    interview_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start an interview session and get the first question."""
    interview = await get_interview_by_id(db, interview_id, current_user.id)
    if not interview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")
    if interview.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview has already been started or completed",
        )

    result = await start_interview_session(db, interview)
    return QuestionResponse(
        question=result["question"],
        question_number=result["question_number"],
        difficulty=result["difficulty"],
    )


@router.post("/{interview_id}/answer", response_model=QuestionResponse)
async def submit_answer(
    interview_id: UUID,
    body: AnswerSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit an answer and get the next question or final report."""
    interview = await get_interview_by_id(db, interview_id, current_user.id)
    if not interview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")
    if interview.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview is not in progress",
        )

    result = await process_answer(db, interview, body.answer)

    return QuestionResponse(
        question=result.get("question", ""),
        question_number=result.get("question_number", 0),
        difficulty=result.get("difficulty", interview.difficulty),
        evaluation=result.get("evaluation"),
        current_score=result.get("current_score"),
        is_finished=result.get("is_finished", False),
        final_report=result.get("final_report"),
    )


@router.post("/{interview_id}/answer/voice", response_model=QuestionResponse)
async def submit_voice_answer(
    interview_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a voice answer (transcribed via speech endpoint first)."""
    # Voice answers are first transcribed via /api/v1/speech/transcribe
    # Then submitted as text here. This endpoint is a convenience wrapper.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Use /speech/transcribe first, then submit text via /answer",
    )


@router.post("/{interview_id}/end")
async def end_interview_early(
    interview_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """End an interview early and generate report."""
    interview = await get_interview_by_id(db, interview_id, current_user.id)
    if not interview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")
    if interview.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview is not in progress",
        )

    result = await end_interview(db, interview)
    return {
        "message": "Interview ended",
        "overall_score": result.get("overall_score", 0),
        "questions_answered": result.get("questions_answered", 0),
    }


@router.get("/{interview_id}/questions", response_model=list[InterviewQuestionResponse])
async def get_questions(
    interview_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all questions and answers for an interview."""
    interview = await get_interview_by_id(db, interview_id, current_user.id)
    if not interview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

    questions = await get_interview_questions(db, interview.id)
    return questions
