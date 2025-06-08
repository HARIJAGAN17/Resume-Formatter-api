from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Path, Form, Body
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.model.pdf_file import PDFFile
from app.schema.pdf_file_schema import PDFFileResponse
from app.utils.resume_reader import convert_doc_bytes_to_pdf_bytes
from typing import List
import base64
from datetime import datetime
import pytz

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload-pdf", response_model=PDFFileResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    db: Session = Depends(get_db)
):
    file_ext = file.filename.lower().split(".")[-1]
    supported_formats = ["pdf", "docx", "doc"]

    if file_ext not in supported_formats:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and DOC files are supported")

    file_bytes = await file.read()

    if file_ext in ["docx", "doc"]:
        try:
            pdf_bytes = convert_doc_bytes_to_pdf_bytes(file_bytes, suffix=f".{file_ext}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to convert {file_ext} to PDF: {str(e)}")
        stored_filename = file.filename.rsplit(".", 1)[0] + ".pdf"
    else:
        pdf_bytes = file_bytes
        stored_filename = file.filename

    uploaded_timestamp =datetime.now(pytz.timezone("Asia/Kolkata")).isoformat()

    new_pdf = PDFFile(
        project_id=project_id,
        file_name=stored_filename,
        file_data=pdf_bytes,
        file_uploaded_timestamp=uploaded_timestamp,
        analysis_status="pending"  # Default status on upload
    )

    db.add(new_pdf)
    db.commit()
    db.refresh(new_pdf)

    return {
        "id": new_pdf.id,
        "project_id": new_pdf.project_id,
        "file_name": new_pdf.file_name,
        "file_uploaded_timestamp": new_pdf.file_uploaded_timestamp,
        "file_data": base64.b64encode(new_pdf.file_data).decode("utf-8"),
        "analysis_status": new_pdf.analysis_status
    }


@router.get("/get-pdfs-by-project/{project_id}", response_model=List[PDFFileResponse])
def get_pdfs_by_project(project_id: int = Path(...), db: Session = Depends(get_db)):
    pdfs = db.query(PDFFile).filter(PDFFile.project_id == project_id).all()
    return [
        {
            "id": pdf.id,
            "project_id": pdf.project_id,
            "file_name": pdf.file_name,
            "file_uploaded_timestamp": pdf.file_uploaded_timestamp,
            "file_data": base64.b64encode(pdf.file_data).decode("utf-8"),
            "analysis_status": pdf.analysis_status
        }
        for pdf in pdfs
    ]


@router.get("/all-pdfs", response_model=List[PDFFileResponse])
def get_all_pdfs(db: Session = Depends(get_db)):
    pdfs = db.query(PDFFile).all()
    return [
        {
            "id": pdf.id,
            "project_id": pdf.project_id,
            "file_name": pdf.file_name,
            "file_uploaded_timestamp": pdf.file_uploaded_timestamp,
            "file_data": base64.b64encode(pdf.file_data).decode("utf-8"),
            "analysis_status": pdf.analysis_status
        }
        for pdf in pdfs
    ]


@router.patch("/update-analysis-status/{pdf_id}", response_model=PDFFileResponse)
def update_analysis_status(
    pdf_id: int,
    analysis_status: str = Body(...),
    db: Session = Depends(get_db)
):
    pdf = db.query(PDFFile).filter(PDFFile.id == pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF file not found")

    pdf.analysis_status = analysis_status
    db.commit()
    db.refresh(pdf)

    return {
        "id": pdf.id,
        "project_id": pdf.project_id,
        "file_name": pdf.file_name,
        "file_uploaded_timestamp": pdf.file_uploaded_timestamp,
        "file_data": base64.b64encode(pdf.file_data).decode("utf-8"),
        "analysis_status": pdf.analysis_status
    }
