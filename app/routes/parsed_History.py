from fastapi import APIRouter, Depends, HTTPException, Path,Body
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.model.parsed_resume import ParsedResume
from app.schema.parsed_resume_job import ParsedResumeCreate, ParsedResumeOut

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/parsed-history", response_model=ParsedResumeOut)
def create_parsed_history(resume: ParsedResumeCreate, db: Session = Depends(get_db)):
    db_resume = ParsedResume(
        project_id=resume.project_id,
        user_id=resume.user_id,
        file_id = resume.file_id,
        resume_name=resume.resume_name,
        resume_details=resume.resume_details,
        formatted_details = resume.formatted_details,
        resume_score=resume.resume_score,
        file_size =resume.file_size,
        summary_analysis=resume.summary_analysis,
        last_analyzed_timestamp= resume.last_analyzed_timestamp,
        approval_status = resume.approval_status

    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

@router.get("/parsed-history", response_model=list[ParsedResumeOut])
def list_parsed_history(db: Session = Depends(get_db)):
    return db.query(ParsedResume).all()

@router.get("/parsed-history/{project_id}", response_model=list[ParsedResumeOut])
def get_parsed_history_by_project(
    project_id: int = Path(..., title="The ID of the project to fetch parsed resumes for"),
    db: Session = Depends(get_db)
):
    resumes = db.query(ParsedResume).filter(ParsedResume.project_id == project_id).all()
    if not resumes:
        raise HTTPException(status_code=404, detail="No parsed resumes found for this project")
    return resumes

@router.put("/parsed-history/file/{file_id}", response_model=ParsedResumeOut)
def update_formatted_details_by_file(
    file_id: int = Path(..., title="The file ID of the parsed resume to update"),
    formatted_details: dict = Body(..., embed=True, description="New formatted details JSON"),
    db: Session = Depends(get_db)
):
    db_resume = db.query(ParsedResume).filter(ParsedResume.file_id == file_id).first()
    if not db_resume:
        raise HTTPException(status_code=404, detail="Parsed resume not found for given file_id")
    
    db_resume.formatted_details = formatted_details
    db.commit()
    db.refresh(db_resume)
    return db_resume
