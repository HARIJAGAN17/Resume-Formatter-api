from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.db import Base  

class ParsedResume(Base):
    __tablename__ = "parsed_resumes"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    resume_name = Column(String, nullable=False)
    resume_details = Column(JSON, nullable=False)
    formatted_details = Column(JSON, nullable=False)
    resume_score = Column(Float, nullable=False)
    summary_analysis = Column(String, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="resumes")
    user = relationship("User", back_populates="resumes")
