"""
InterviewGPT — Resume Pydantic Schemas
"""

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class ParsedResumeData(BaseModel):
    name: Optional[str] = None
    skills: List[str] = []
    education: List[dict] = []
    experience: List[dict] = []
    projects: List[dict] = []
    certifications: List[str] = []


class ResumeResponse(BaseModel):
    id: UUID
    user_id: UUID
    file_name: str
    file_type: str
    parsed_data: Optional[dict] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeListResponse(BaseModel):
    resumes: List[ResumeResponse]
    total: int


class ResumeDetailResponse(ResumeResponse):
    raw_text: Optional[str] = None
    chromadb_collection_id: Optional[str] = None
