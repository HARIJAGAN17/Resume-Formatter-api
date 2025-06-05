from pydantic import BaseModel
from datetime import date
from typing import Optional


class ProjectBase(BaseModel):
    name: str
    project_description: str
    job_description: str
    job_title: str
    resume_count: int
    threshold: int



class ProjectCreate(ProjectBase):
    user_id: int

class ProjectResponse(ProjectBase):
    id: int
    status: str = "Active"
    user_id: int
    created_at: date 

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    project_description: Optional[str] = None
    job_description: Optional[str] = None
    job_title: Optional[str] = None
    resume_count: Optional[int] = None
    threshold: Optional[int] = None
    status: Optional[str] = None
    user_id: Optional[int] = None  # O

    class Config:
        orm_mode = True