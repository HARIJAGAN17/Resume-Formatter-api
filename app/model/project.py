from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy.sql import func
from app.database.db import Base
from sqlalchemy.orm import relationship


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    project_description = Column(String)
    job_description = Column(String)
    job_title = Column(String)
    resume_count = Column(Integer, default=0)
    status = Column(String, default="Active")
    created_at = Column(Date, default=func.current_date())
    threshold = Column(Integer)

    resumes = relationship("ParsedResume", back_populates="project", cascade="all, delete")