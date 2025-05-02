import json
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.resume_reader import extract_resume_text
from app.gpt_model.resume_parser import extract_resume_data

router = APIRouter()

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX files are allowed")

    file_bytes = await file.read()
    text = extract_resume_text(file_bytes, file.filename)

    if not text:
        raise HTTPException(status_code=400, detail="Failed to extract resume text")

    gpt_response = extract_resume_data(text)
    print("Raw GPT Response:", gpt_response)

    gpt_text = gpt_response.get("response", "")

    # Strip common markdown formatting from OpenAI responses
    cleaned = gpt_text.strip("`").strip()
    if cleaned.startswith("json"):
        cleaned = cleaned[len("json"):].strip()

    try:
        structured_data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("JSON Error:", e)
        raise HTTPException(status_code=500, detail="Invalid JSON from GPT response")

    return structured_data
