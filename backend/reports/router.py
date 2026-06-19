"""
InterviewGPT — Reports API Router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from database import get_db
from database.models import User
from auth.dependencies import get_current_user
from reports.schemas import ReportResponse
from reports.service import get_report_by_interview, get_user_reports
from reports.pdf_generator import generate_pdf_report

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/", response_model=list[ReportResponse])
async def list_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all reports for the current user."""
    reports = await get_user_reports(db, current_user.id)
    return reports


@router.get("/{interview_id}", response_model=ReportResponse)
async def get_report(
    interview_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get interview report."""
    report = await get_report_by_interview(db, interview_id, current_user.id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report


@router.get("/{interview_id}/pdf")
async def download_pdf_report(
    interview_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download interview report as PDF."""
    report = await get_report_by_interview(db, interview_id, current_user.id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    # Check if PDF already exists
    if report.pdf_path:
        import os
        if os.path.exists(report.pdf_path):
            return FileResponse(
                report.pdf_path,
                media_type="application/pdf",
                filename=f"interview_report_{str(interview_id)[:8]}.pdf",
            )

    # Generate PDF
    report_data = {
        "executive_summary": report.executive_summary,
        "technical_assessment": report.technical_assessment,
        "behavioral_assessment": report.behavioral_assessment,
        "project_knowledge": report.project_knowledge,
        "communication_skills": report.communication_skills,
        "improvement_areas": report.improvement_areas,
        "learning_path": report.learning_path,
        "overall_score": report.overall_score,
        "overall_grade": report.overall_grade,
    }

    from interviews.service import get_interview_by_id
    interview = await get_interview_by_id(db, interview_id, current_user.id)
    interview_data = {
        "target_role": interview.target_role if interview else "",
        "interview_type": interview.interview_type if interview else "",
        "duration_minutes": interview.duration_minutes if interview else 0,
    }

    pdf_path = await generate_pdf_report(report_data, interview_data)
    report.pdf_path = pdf_path
    await db.flush()

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"interview_report_{str(interview_id)[:8]}.pdf",
    )
