from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy.sql import func
from app.database.db import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    job_title = Column(String)
    resume_count = Column(Integer, default=0)
    avg_score = Column(Float, default=0.0)
    status = Column(String, default="Active")
    created_at = Column(Date, default=func.current_date())
    threshold = Column(Integer)