"""
InterviewGPT — Users API Router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from backend.database import get_db
from backend.database.models import User
from backend.users.schemas import UserResponse, UserUpdate
from backend.users.service import get_all_users, update_user_role
from backend.auth.dependencies import get_current_user, get_current_admin

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    updates: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user's profile."""
    if updates.full_name:
        current_user.full_name = updates.full_name
    if updates.avatar_url is not None:
        current_user.avatar_url = updates.avatar_url
    await db.flush()
    await db.refresh(current_user)
    return current_user
