# routes/pdf_upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.model.pdf_file import PDFFile
from app.schema.pdf_file_schema import PDFFileResponse
from app.utils.resume_reader import convert_doc_bytes_to_pdf_bytes

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload-pdf", response_model=PDFFileResponse)
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_ext = file.filename.lower().split(".")[-1]
    supported_formats = ["pdf", "docx", "doc"]

    if file_ext not in supported_formats:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and DOC files are supported")

    file_bytes = await file.read()

    # Convert DOCX/DOC to PDF bytes
    if file_ext in ["docx", "doc"]:
        try:
            pdf_bytes = convert_doc_bytes_to_pdf_bytes(file_bytes, suffix=f".{file_ext}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to convert {file_ext} to PDF: {str(e)}")
        stored_filename = file.filename.rsplit(".", 1)[0] + ".pdf"
    else:
        pdf_bytes = file_bytes
        stored_filename = file.filename

    new_pdf = PDFFile(
        file_name=stored_filename,
        file_data=pdf_bytes
    )

    db.add(new_pdf)
    db.commit()
    db.refresh(new_pdf)

    return new_pdf
