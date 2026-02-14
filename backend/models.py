from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class WorkerBase(BaseModel):
    name: str = Field(..., min_length=1)
    skill: str = Field(..., min_length=1, description="Primary trade, e.g., Mason, Carpenter")
    rating: float = Field(ge=0, le=5, default=4.0)
    availability: str = Field(
        default="Available",
        description="Simple availability flag such as 'Available' or 'Busy'",
    )
    owner_uid: Optional[str] = Field(
        default=None,
        description="Firebase Auth UID of the creator (optional in v1)",
    )
    phone: Optional[str] = Field(default=None, description="Contact phone for Call")
    email: Optional[str] = Field(default=None, description="Contact email")
    portfolio_link: Optional[str] = Field(default=None, description="Optional portfolio/website URL")


class WorkerCreate(WorkerBase):
    pass


class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    skill: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    availability: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    portfolio_link: Optional[str] = None


class Worker(WorkerBase):
    id: str
    created_at: int = Field(
        default_factory=lambda: int(datetime.utcnow().timestamp()),
        description="Unix timestamp used for simple sorting",
    )


class RecommendationResult(BaseModel):
    workers: List[Worker]
