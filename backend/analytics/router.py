"""
InterviewGPT — Analytics API Router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.database.models import User
from backend.auth.dependencies import get_current_user, get_current_admin
from backend.analytics.service import get_dashboard_data, get_admin_stats

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics dashboard data for the current user."""
    data = await get_dashboard_data(db, current_user.id)
    return data


@router.get("/trends")
async def get_trends(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get score trends over time."""
    data = await get_dashboard_data(db, current_user.id)
    return {
        "recent_scores": data["recent_scores"],
        "score_by_type": data["score_by_type"],
    }


@router.get("/skills")
async def get_skills(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get skill heatmap data."""
    data = await get_dashboard_data(db, current_user.id)
    return {"skill_scores": data["skill_scores"]}
