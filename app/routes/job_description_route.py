from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from app.authentication.auth import get_current_user
from app.model.user_auth import User
from app.utils.resume_reader import convert_doc_bytes_to_pdf_bytes,extract_text_from_pdf_bytes
import os

router = APIRouter()

@router.post("/job-description-extraction")
async def job_description_extraction(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    filename = file.filename.lower()

    if not filename.endswith((".pdf", ".docx", ".doc", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, DOC or TXT files are allowed")

    file_bytes = await file.read()

    if await request.is_disconnected():
        raise HTTPException(status_code=499, detail="Client disconnected during upload")

    extracted_text = ""

    try:
        if filename.endswith(".txt"):
            extracted_text = file_bytes.decode("utf-8", errors="ignore")

        elif filename.endswith(".pdf"):
            extracted_text = extract_text_from_pdf_bytes(file_bytes)

        elif filename.endswith((".docx", ".doc")):
            pdf_bytes = convert_doc_bytes_to_pdf_bytes(file_bytes, suffix=os.path.splitext(filename)[1])
            extracted_text = extract_text_from_pdf_bytes(pdf_bytes)

    except Exception as e:
        print("Extraction error:", e)
        raise HTTPException(status_code=500, detail="Failed to extract job description from file")

    cleaned_text = " ".join(extracted_text.split()).strip()
    return {"job_description": cleaned_text}

