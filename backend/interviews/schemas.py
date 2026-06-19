"""
InterviewGPT — Interview Pydantic Schemas
"""

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class InterviewCreate(BaseModel):
    target_role: str = Field(..., description="Target job role")
    interview_type: str = Field(..., description="hr, technical, dsa, system_design, project_discussion")
    difficulty: str = Field(..., description="beginner, intermediate, advanced")
    duration_minutes: int = Field(..., ge=15, le=60)
    resume_id: Optional[UUID] = None
    company: Optional[str] = None


class InterviewResponse(BaseModel):
    id: UUID
    user_id: UUID
    resume_id: Optional[UUID] = None
    target_role: str
    interview_type: str
    difficulty: str
    duration_minutes: int
    company: Optional[str] = None
    status: str
    current_score: float
    total_questions: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InterviewListResponse(BaseModel):
    interviews: List[InterviewResponse]
    total: int


class AnswerSubmit(BaseModel):
    answer: str = Field(..., min_length=1)


class QuestionResponse(BaseModel):
    question: str
    question_number: int
    difficulty: str
    evaluation: Optional[dict] = None
    current_score: Optional[float] = None
    is_finished: bool = False
    final_report: Optional[dict] = None


class InterviewQuestionResponse(BaseModel):
    id: UUID
    question_number: int
    question_text: str
    question_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    candidate_answer: Optional[str] = None
    answer_mode: str = "text"
    ai_evaluation: Optional[dict] = None
    score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
