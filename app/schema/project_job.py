from pydantic import BaseModel
from datetime import date

class ProjectBase(BaseModel):
    name: str
    description: str
    job_title: str
    resume_count: int
    threshold: int



class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    status: str = "Active"
    created_at: date 

    class Config:
        orm_mode = True