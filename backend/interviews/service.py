"""
InterviewGPT — Interview Service
"""
from __future__ import annotations


from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import Interview, InterviewQuestion, Report
from backend.interviews.schemas import InterviewCreate
from backend.llm.agent import start_interview, submit_answer, end_interview_early, calculate_max_questions
from backend.resumes.service import get_active_resume, get_resume_by_id


async def create_interview(
    db: AsyncSession,
    user_id: UUID,
    data: InterviewCreate,
) -> Interview:
    """Create a new interview session."""
    # Get resume
    if data.resume_id:
        resume = await get_resume_by_id(db, data.resume_id, user_id)
    else:
        resume = await get_active_resume(db, user_id)

    interview = Interview(
        user_id=user_id,
        resume_id=resume.id if resume else None,
        target_role=data.target_role,
        interview_type=data.interview_type,
        difficulty=data.difficulty,
        duration_minutes=data.duration_minutes,
        company=data.company,
        status="pending",
    )
    db.add(interview)
    await db.flush()
    await db.refresh(interview)
    return interview


async def start_interview_session(
    db: AsyncSession,
    interview: Interview,
) -> dict:
    """Start the interview and get the first question."""
    max_questions = calculate_max_questions(interview.duration_minutes)

    result = await start_interview(
        user_id=str(interview.user_id),
        target_role=interview.target_role,
        interview_type=interview.interview_type,
        difficulty=interview.difficulty,
        max_questions=max_questions,
        company=interview.company,
    )

    # Update interview status
    interview.status = "in_progress"
    interview.started_at = datetime.utcnow()
    interview.agent_state = result["agent_state"]
    interview.total_questions = 1

    # Save first question
    question = InterviewQuestion(
        interview_id=interview.id,
        question_number=1,
        question_text=result["question"],
        question_type=interview.interview_type,
        difficulty_level=result["difficulty"],
    )
    db.add(question)
    await db.flush()

    return result


async def process_answer(
    db: AsyncSession,
    interview: Interview,
    answer_text: str,
    answer_mode: str = "text",
) -> dict:
    """Process a candidate's answer and get the next question or report."""
    # Submit answer to the agent
    result = await submit_answer(interview.agent_state, answer_text)

    # Update the current question with the answer
    current_q = await db.execute(
        select(InterviewQuestion)
        .where(
            InterviewQuestion.interview_id == interview.id,
            InterviewQuestion.question_number == interview.total_questions,
        )
    )
    question_record = current_q.scalars().first()
    if question_record:
        question_record.candidate_answer = answer_text
        question_record.answer_mode = answer_mode
        question_record.ai_evaluation = result.get("evaluation")
        question_record.score = result.get("evaluation", {}).get("score")

    # Update interview state
    interview.agent_state = result["agent_state"]
    interview.current_score = result.get("current_score", interview.current_score)

    if result.get("is_finished"):
        interview.status = "completed"
        interview.completed_at = datetime.utcnow()

        # Save report
        if result.get("final_report"):
            report = Report(
                interview_id=interview.id,
                user_id=interview.user_id,
                executive_summary=result["final_report"].get("executive_summary"),
                technical_assessment=result["final_report"].get("technical_assessment"),
                behavioral_assessment=result["final_report"].get("behavioral_assessment"),
                project_knowledge=result["final_report"].get("project_knowledge"),
                communication_skills=result["final_report"].get("communication_skills"),
                improvement_areas=result["final_report"].get("improvement_areas"),
                learning_path=result["final_report"].get("learning_path"),
                overall_score=interview.current_score,
                overall_grade=result["final_report"].get("overall_grade", "C"),
            )
            db.add(report)
    else:
        # Save next question
        interview.total_questions += 1
        next_question = InterviewQuestion(
            interview_id=interview.id,
            question_number=result["question_number"],
            question_text=result["question"],
            question_type=interview.interview_type,
            difficulty_level=result["difficulty"],
        )
        db.add(next_question)

    await db.flush()
    return result


async def end_interview(db: AsyncSession, interview: Interview) -> dict:
    """End an interview early and generate report."""
    result = await end_interview_early(interview.agent_state)

    interview.status = "completed"
    interview.completed_at = datetime.utcnow()
    interview.agent_state = result["agent_state"]

    if result.get("final_report"):
        report = Report(
            interview_id=interview.id,
            user_id=interview.user_id,
            executive_summary=result["final_report"].get("executive_summary"),
            technical_assessment=result["final_report"].get("technical_assessment"),
            behavioral_assessment=result["final_report"].get("behavioral_assessment"),
            project_knowledge=result["final_report"].get("project_knowledge"),
            communication_skills=result["final_report"].get("communication_skills"),
            improvement_areas=result["final_report"].get("improvement_areas"),
            learning_path=result["final_report"].get("learning_path"),
            overall_score=interview.current_score,
            overall_grade=result["final_report"].get("overall_grade", "C"),
        )
        db.add(report)

    await db.flush()
    return result


async def get_user_interviews(db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 20):
    result = await db.execute(
        select(Interview)
        .where(Interview.user_id == user_id)
        .order_by(Interview.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_interview_by_id(db: AsyncSession, interview_id: UUID, user_id: UUID) -> Interview | None:
    result = await db.execute(
        select(Interview).where(Interview.id == interview_id, Interview.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_interview_questions(db: AsyncSession, interview_id: UUID):
    result = await db.execute(
        select(InterviewQuestion)
        .where(InterviewQuestion.interview_id == interview_id)
        .order_by(InterviewQuestion.question_number)
    )
    return result.scalars().all()


async def get_interview_count(db: AsyncSession, user_id: UUID | None = None) -> int:
    query = select(func.count(Interview.id))
    if user_id:
        query = query.where(Interview.user_id == user_id)
    result = await db.execute(query)
    return result.scalar_one()
