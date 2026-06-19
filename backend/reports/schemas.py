"""
InterviewGPT — Report Schemas
"""

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class ReportResponse(BaseModel):
    id: UUID
    interview_id: UUID
    executive_summary: Optional[str] = None
    technical_assessment: Optional[dict] = None
    behavioral_assessment: Optional[dict] = None
    project_knowledge: Optional[dict] = None
    communication_skills: Optional[dict] = None
    improvement_areas: Optional[list] = None
    learning_path: Optional[list] = None
    overall_score: Optional[float] = None
    overall_grade: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
