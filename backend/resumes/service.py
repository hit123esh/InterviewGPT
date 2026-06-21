"""
InterviewGPT — Resume Service
"""
from __future__ import annotations


import os
import uuid
import aiofiles
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import Resume
from backend.resumes.parser import extract_text, parse_resume_with_ai
from backend.config import get_settings

settings = get_settings()


async def save_uploaded_file(file_bytes: bytes, filename: str) -> str:
    """Save uploaded file to disk and return the path."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    unique_name = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_name)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file_bytes)
    return file_path


async def process_resume(
    db: AsyncSession,
    user_id: UUID,
    file_bytes: bytes,
    filename: str,
    file_type: str,
) -> Resume:
    """Upload, parse, and store a resume."""
    # Save file
    file_path = await save_uploaded_file(file_bytes, filename)

    # Extract raw text
    raw_text = extract_text(file_bytes, file_type)

    # AI-powered structured extraction
    parsed_data = await parse_resume_with_ai(raw_text)

    # Deactivate previous resumes
    result = await db.execute(
        select(Resume).where(Resume.user_id == user_id, Resume.is_active == True)
    )
    for old_resume in result.scalars().all():
        old_resume.is_active = False

    # Create new resume record
    resume = Resume(
        user_id=user_id,
        file_name=filename,
        file_path=file_path,
        file_type=file_type,
        raw_text=raw_text,
        parsed_data=parsed_data,
        is_active=True,
    )
    db.add(resume)
    await db.flush()
    await db.refresh(resume)

    # Index in ChromaDB (async, non-blocking)
    try:
        from backend.rag.embeddings import index_resume
        await index_resume(resume)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"ChromaDB indexing failed: {e}")

    return resume


async def get_user_resumes(db: AsyncSession, user_id: UUID):
    result = await db.execute(
        select(Resume).where(Resume.user_id == user_id).order_by(Resume.created_at.desc())
    )
    return result.scalars().all()


async def get_resume_by_id(db: AsyncSession, resume_id: UUID, user_id: UUID) -> Resume | None:
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_active_resume(db: AsyncSession, user_id: UUID) -> Resume | None:
    result = await db.execute(
        select(Resume).where(Resume.user_id == user_id, Resume.is_active == True)
    )
    return result.scalar_one_or_none()


async def delete_resume(db: AsyncSession, resume_id: UUID, user_id: UUID) -> bool:
    resume = await get_resume_by_id(db, resume_id, user_id)
    if not resume:
        return False
    # Delete file from disk
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    await db.delete(resume)
    return True
