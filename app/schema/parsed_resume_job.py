from pydantic import BaseModel
from typing import Any

class ParsedResumeBase(BaseModel):
    resume_name: str
    resume_details: dict 
    formatted_details: dict
    resume_score: float
    file_size: float
    summary_analysis: list[str] | None = None  # <-- changed to list of strings (JSON)
    last_analyzed_timestamp: str | None = None
    approval_status: str | None = None

class ParsedResumeCreate(ParsedResumeBase):
    project_id: int
    user_id: int

class ParsedResumeOut(ParsedResumeBase):
    id: int
    project_id: int
    user_id: int
