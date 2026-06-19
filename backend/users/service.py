"""
InterviewGPT — Users Service
"""
from __future__ import annotations


from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User


async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 50):
    result = await db.execute(
        select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    )
    return result.scalars().all()


async def get_user_count(db: AsyncSession) -> int:
    result = await db.execute(select(func.count(User.id)))
    return result.scalar_one()


async def update_user_role(db: AsyncSession, user_id: UUID, role: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.role = role
        await db.flush()
        await db.refresh(user)
    return user
