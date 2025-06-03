from pydantic import BaseModel
from typing import Any

class ParsedResumeBase(BaseModel):
    resume_name: str
    resume_details: dict 
    formatted_details: dict
    resume_score: float
    summary_analysis: str | None = None

class ParsedResumeCreate(ParsedResumeBase):
    project_id: int
    user_id: int

class ParsedResumeOut(ParsedResumeBase):
    id: int
    project_id: int
    user_id: int

    class Config:
        orm_mode = True
