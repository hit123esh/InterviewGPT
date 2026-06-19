"""
InterviewGPT — Report Service
"""
from __future__ import annotations


from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Report, Interview, InterviewQuestion


async def get_report_by_interview(db: AsyncSession, interview_id: UUID, user_id: UUID) -> Report | None:
    result = await db.execute(
        select(Report).where(
            Report.interview_id == interview_id,
            Report.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def get_user_reports(db: AsyncSession, user_id: UUID):
    result = await db.execute(
        select(Report)
        .where(Report.user_id == user_id)
        .order_by(Report.created_at.desc())
    )
    return result.scalars().all()
