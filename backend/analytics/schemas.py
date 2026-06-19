"""
InterviewGPT — Analytics Schemas
"""

from pydantic import BaseModel
from typing import List, Optional


class DashboardStats(BaseModel):
    total_interviews: int
    completed_interviews: int
    average_score: float
    best_score: float
    total_questions_answered: int
    most_practiced_type: Optional[str] = None


class ScoreTrend(BaseModel):
    date: str
    score: float
    interview_type: str


class SkillScore(BaseModel):
    skill: str
    score: float
    count: int


class DashboardResponse(BaseModel):
    stats: DashboardStats
    recent_scores: List[ScoreTrend]
    skill_scores: List[SkillScore]
    interview_type_distribution: dict
    score_by_type: dict
