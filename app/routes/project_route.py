from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app.model.project import Project
from app.schema.project_job import ProjectCreate, ProjectResponse, ProjectStatusUpdate
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
def create_new_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(
        user_id = project.user_id,
        name=project.name,
        project_description = project.project_description,
        job_description = project.job_description,
        job_title=project.job_title,
        resume_count=project.resume_count,
        threshold=project.threshold
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/projects", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project_by_id(
    project_id: int = Path(..., title="The ID of the project to get"),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/projects/{project_id}/status", response_model=ProjectResponse)
def update_project_status(
    project_id: int,
    status_data: ProjectStatusUpdate,  # Now expecting a Pydantic model
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.status = status_data.status  # access the field from model

    db.commit()
    db.refresh(project)
    return project




@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"detail": f"Project with ID {project_id} deleted successfully"}