"""
InterviewGPT — SQLAlchemy ORM Models
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float,
    ForeignKey, DateTime, JSON, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), default="candidate", nullable=False)
    avatar_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(role.in_(["candidate", "admin"]), name="check_user_role"),
    )

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_type = Column(String(10), nullable=False)
    raw_text = Column(Text, nullable=True)
    parsed_data = Column(JSON, nullable=True)
    chromadb_collection_id = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="resumes")
    interviews = relationship("Interview", back_populates="resume")


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=True)
    target_role = Column(String(100), nullable=False)
    interview_type = Column(String(50), nullable=False)
    difficulty = Column(String(20), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    company = Column(String(50), nullable=True)
    status = Column(String(20), default="pending")
    current_score = Column(Float, default=0.0)
    total_questions = Column(Integer, default=0)
    agent_state = Column(JSON, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            status.in_(["pending", "in_progress", "completed", "cancelled"]),
            name="check_interview_status"
        ),
    )

    # Relationships
    user = relationship("User", back_populates="interviews")
    resume = relationship("Resume", back_populates="interviews")
    questions = relationship("InterviewQuestion", back_populates="interview", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="interview", uselist=False)


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_id = Column(UUID(as_uuid=True), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=True)
    difficulty_level = Column(String(20), nullable=True)
    candidate_answer = Column(Text, nullable=True)
    answer_mode = Column(String(20), default="text")
    voice_transcript = Column(Text, nullable=True)
    ai_evaluation = Column(JSON, nullable=True)
    score = Column(Float, nullable=True)
    follow_up_of = Column(UUID(as_uuid=True), ForeignKey("interview_questions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interview = relationship("Interview", back_populates="questions")
    coding_submissions = relationship("CodingSubmission", back_populates="question", cascade="all, delete-orphan")
    follow_up_parent = relationship("InterviewQuestion", remote_side=[id])


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_id = Column(UUID(as_uuid=True), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    executive_summary = Column(Text, nullable=True)
    technical_assessment = Column(JSON, nullable=True)
    behavioral_assessment = Column(JSON, nullable=True)
    project_knowledge = Column(JSON, nullable=True)
    communication_skills = Column(JSON, nullable=True)
    improvement_areas = Column(JSON, nullable=True)
    learning_path = Column(JSON, nullable=True)
    overall_score = Column(Float, nullable=True)
    overall_grade = Column(String(5), nullable=True)
    pdf_path = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interview = relationship("Interview", back_populates="report")
    user = relationship("User", back_populates="reports")


class CodingSubmission(Base):
    __tablename__ = "coding_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False)
    language = Column(String(20), nullable=False)
    code = Column(Text, nullable=False)
    test_results = Column(JSON, nullable=True)
    correctness_score = Column(Float, nullable=True)
    efficiency_score = Column(Float, nullable=True)
    ai_feedback = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    question = relationship("InterviewQuestion", back_populates="coding_submissions")
