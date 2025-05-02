from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.resume_reader import extract_resume_text
from app.gpt_model.resume_parser import extract_resume_data

router = APIRouter()

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX allowed")

    file_bytes = await file.read()
    text = extract_resume_text(file_bytes, file.filename)

    if not text:
        raise HTTPException(status_code=400, detail="Failed to extract text")

    gpt_response = extract_resume_data(text)

    return {"structured_resume": gpt_response}
