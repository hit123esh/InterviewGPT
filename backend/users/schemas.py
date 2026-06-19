"""
InterviewGPT — Users Schemas
"""

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[str] = None
