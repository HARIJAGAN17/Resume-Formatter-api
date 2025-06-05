from pydantic import BaseModel
from datetime import date

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

    class Config:
        orm_mode = True