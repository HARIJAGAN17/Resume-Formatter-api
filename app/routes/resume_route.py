import json
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.authentication.auth import get_current_user
from app.model.user_auth import User
from app.utils.resume_reader import convert_doc_bytes_to_pdf_bytes, convert_pdf_to_image_bytes
from app.gpt_model.resume_parser import extract_resume_data_from_image
import tiktoken
import os

router = APIRouter()

# Count tokens
def count_tokens(text: str, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Score based on field completeness
def experience_completeness_score(exp):
    score = 0
    if exp.get("company"): score += 1
    if exp.get("date"): score += 1
    if exp.get("role"): score += 1
    if exp.get("clientEngagement"): score += 1
    if exp.get("program"): score += 1
    if exp.get("responsibilities") and len(exp["responsibilities"]) > 0: score += 1
    return score

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    if not file.filename.endswith((".pdf", ".docx", ".doc")):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX or DOC files are allowed")

    file_bytes = await file.read()

    # Convert to PDF if necessary
    if file.filename.endswith(".pdf"):
        pdf_bytes = file_bytes
    else:
        pdf_bytes = convert_doc_bytes_to_pdf_bytes(file_bytes, suffix=os.path.splitext(file.filename)[1])

    # Convert PDF to images
    image_bytes_list = convert_pdf_to_image_bytes(pdf_bytes)

    # Send to GPT-4o (vision) for parsing
    gpt_response = extract_resume_data_from_image(image_bytes_list)

    gpt_text = gpt_response.get("response", "")
    cleaned = gpt_text.strip("`").strip()
    if cleaned.startswith("json"):
        cleaned = cleaned[len("json"):].strip()

    try:
        structured_data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("JSON Error:", e)
        raise HTTPException(status_code=500, detail="Invalid JSON from GPT response")

    # 🔽 Sort experience by completeness
    if "experience" in structured_data:
        structured_data["experience"].sort(key=experience_completeness_score, reverse=True)

    return structured_data
