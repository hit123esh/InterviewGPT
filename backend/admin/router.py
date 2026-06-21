"""
InterviewGPT — Admin API Router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from backend.database import get_db
from backend.database.models import User
from backend.auth.dependencies import get_current_admin
from backend.users.schemas import UserResponse
from backend.users.service import get_all_users, update_user_role
from backend.analytics.service import get_admin_stats
from backend.interviews.service import get_user_interviews

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[UserResponse])
async def list_all_users(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all users (admin only)."""
    users = await get_all_users(db, skip, limit)
    return users


@router.patch("/users/{user_id}", response_model=UserResponse)
async def change_user_role(
    user_id: UUID,
    role: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update a user's role (admin only)."""
    if role not in ["candidate", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'candidate' or 'admin'",
        )
    user = await update_user_role(db, user_id, role)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/stats")
async def get_platform_stats(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get platform-wide statistics (admin only)."""
    stats = await get_admin_stats(db)
    return stats


@router.get("/interviews")
async def get_all_interviews(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all interview sessions (admin only)."""
    from sqlalchemy import select
    from backend.database.models import Interview
    result = await db.execute(
        select(Interview).order_by(Interview.created_at.desc()).offset(skip).limit(limit)
    )
    interviews = result.scalars().all()
    return [
        {
            "id": str(i.id),
            "user_id": str(i.user_id),
            "target_role": i.target_role,
            "interview_type": i.interview_type,
            "status": i.status,
            "current_score": i.current_score,
            "created_at": i.created_at.isoformat(),
        }
        for i in interviews
    ]
