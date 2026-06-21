"""
InterviewGPT — Resume API Router
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from backend.database import get_db
from backend.database.models import User
from backend.auth.dependencies import get_current_user
from backend.resumes.schemas import ResumeResponse, ResumeListResponse, ResumeDetailResponse
from backend.resumes.service import (
    process_resume, get_user_resumes, get_resume_by_id, delete_resume
)
from backend.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/resumes", tags=["Resumes"])

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload and parse a resume file (PDF or DOCX)."""
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}. Use PDF or DOCX.",
        )

    # Validate file size
    file_bytes = await file.read()
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB.",
        )

    file_type = ALLOWED_TYPES[file.content_type]
    resume = await process_resume(db, current_user.id, file_bytes, file.filename, file_type)
    return resume


@router.get("/", response_model=ResumeListResponse)
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all resumes for the current user."""
    resumes = await get_user_resumes(db, current_user.id)
    return ResumeListResponse(resumes=resumes, total=len(resumes))


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
async def get_resume(
    resume_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed resume information."""
    resume = await get_resume_by_id(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_resume(
    resume_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a resume."""
    deleted = await delete_resume(db, resume_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")


@router.get("/{resume_id}/skills")
async def get_resume_skills(
    resume_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get extracted skills from a resume."""
    resume = await get_resume_by_id(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    skills = resume.parsed_data.get("skills", []) if resume.parsed_data else []
    return {"skills": skills}
