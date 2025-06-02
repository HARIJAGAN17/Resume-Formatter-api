from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.model.project import Project
from app.schema.project_job import ProjectCreate, ProjectResponse
from app.database.db import SessionLocal
from app.authentication.auth import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/projects", response_model=ProjectResponse)
def create_new_project(project: ProjectCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)
):
    db_project = Project(
        name=project.name,
        description=project.description,
        job_title=project.job_title,
        resume_count=project.resume_count,
        avg_score=project.avg_score,
        threshold=project.threshold
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/projects", response_model=list[ProjectResponse])
def list_projects(user: dict = Depends(get_current_user) ,db: Session = Depends(get_db)):
    return db.query(Project).all()