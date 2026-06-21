"""
InterviewGPT — Analytics Service
"""

from uuid import UUID
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import Interview, InterviewQuestion, Report


async def get_dashboard_data(db: AsyncSession, user_id: UUID) -> dict:
    """Get comprehensive analytics dashboard data for a user."""
    
    # Basic stats
    interviews_result = await db.execute(
        select(Interview).where(Interview.user_id == user_id)
    )
    interviews = interviews_result.scalars().all()
    
    completed = [i for i in interviews if i.status == "completed"]
    scores = [i.current_score for i in completed if i.current_score > 0]
    
    stats = {
        "total_interviews": len(interviews),
        "completed_interviews": len(completed),
        "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "best_score": round(max(scores), 1) if scores else 0,
        "total_questions_answered": 0,
        "most_practiced_type": None,
    }

    # Total questions answered
    q_count = await db.execute(
        select(func.count(InterviewQuestion.id))
        .join(Interview)
        .where(Interview.user_id == user_id, InterviewQuestion.candidate_answer.isnot(None))
    )
    stats["total_questions_answered"] = q_count.scalar_one()

    # Most practiced type
    if completed:
        type_counts = {}
        for i in completed:
            type_counts[i.interview_type] = type_counts.get(i.interview_type, 0) + 1
        stats["most_practiced_type"] = max(type_counts, key=type_counts.get) if type_counts else None

    # Score trends (last 20 completed interviews)
    recent_scores = []
    for i in sorted(completed, key=lambda x: x.created_at)[-20:]:
        recent_scores.append({
            "date": i.completed_at.strftime("%Y-%m-%d") if i.completed_at else i.created_at.strftime("%Y-%m-%d"),
            "score": round(i.current_score, 1),
            "interview_type": i.interview_type,
        })

    # Interview type distribution
    type_distribution = {}
    for i in interviews:
        type_distribution[i.interview_type] = type_distribution.get(i.interview_type, 0) + 1

    # Average score by type
    score_by_type = {}
    for i in completed:
        if i.interview_type not in score_by_type:
            score_by_type[i.interview_type] = {"total": 0, "count": 0}
        score_by_type[i.interview_type]["total"] += i.current_score
        score_by_type[i.interview_type]["count"] += 1
    
    for t in score_by_type:
        score_by_type[t] = round(
            score_by_type[t]["total"] / score_by_type[t]["count"], 1
        )

    # Skill scores from evaluations
    skill_scores = await _extract_skill_scores(db, user_id)

    return {
        "stats": stats,
        "recent_scores": recent_scores,
        "skill_scores": skill_scores,
        "interview_type_distribution": type_distribution,
        "score_by_type": score_by_type,
    }


async def _extract_skill_scores(db: AsyncSession, user_id: UUID) -> list:
    """Extract per-skill scores from interview evaluations."""
    questions_result = await db.execute(
        select(InterviewQuestion)
        .join(Interview)
        .where(
            Interview.user_id == user_id,
            InterviewQuestion.ai_evaluation.isnot(None),
        )
    )
    questions = questions_result.scalars().all()
    
    # Aggregate scores by type categories
    type_scores = {}
    for q in questions:
        eval_data = q.ai_evaluation or {}
        score = eval_data.get("score", q.score or 0)
        q_type = q.question_type or "general"
        
        if q_type not in type_scores:
            type_scores[q_type] = {"total": 0, "count": 0}
        type_scores[q_type]["total"] += score
        type_scores[q_type]["count"] += 1

    return [
        {
            "skill": skill.replace("_", " ").title(),
            "score": round(data["total"] / data["count"], 1),
            "count": data["count"],
        }
        for skill, data in type_scores.items()
    ]


async def get_admin_stats(db: AsyncSession) -> dict:
    """Get platform-wide statistics for admin dashboard."""
    from backend.users.service import get_user_count
    
    user_count = await get_user_count(db)
    
    interview_count = await db.execute(select(func.count(Interview.id)))
    total_interviews = interview_count.scalar_one()
    
    completed_count = await db.execute(
        select(func.count(Interview.id)).where(Interview.status == "completed")
    )
    total_completed = completed_count.scalar_one()
    
    avg_score = await db.execute(
        select(func.avg(Interview.current_score)).where(
            Interview.status == "completed",
            Interview.current_score > 0,
        )
    )
    average_score = avg_score.scalar_one() or 0

    return {
        "total_users": user_count,
        "total_interviews": total_interviews,
        "completed_interviews": total_completed,
        "average_score": round(float(average_score), 1),
    }
