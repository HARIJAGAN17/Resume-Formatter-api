from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from app.authentication.auth import get_current_user
from app.model.user_auth import User
from app.utils.resume_reader import convert_doc_bytes_to_pdf_bytes, convert_pdf_to_image_bytes
from app.gpt_model.resume_parser import extract_resume_data_from_image,analyze_resume_from_images
import json
import os
import tiktoken

router = APIRouter()

def count_tokens(text: str, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

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
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith((".pdf", ".docx", ".doc")):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX or DOC files are allowed")

    file_bytes = await file.read()

    if await request.is_disconnected():
        raise HTTPException(status_code=499, detail="Client disconnected during upload")

    if file.filename.endswith(".pdf"):
        pdf_bytes = file_bytes
    else:
        pdf_bytes = convert_doc_bytes_to_pdf_bytes(file_bytes, suffix=os.path.splitext(file.filename)[1])

    if await request.is_disconnected():
        raise HTTPException(status_code=499, detail="Client disconnected before processing")

    image_bytes_list = convert_pdf_to_image_bytes(pdf_bytes)

    if await request.is_disconnected():
        raise HTTPException(status_code=499, detail="Client disconnected before GPT processing")

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

    if "experience" in structured_data:
        structured_data["experience"].sort(key=experience_completeness_score, reverse=True)

    return structured_data

from fastapi import Body

@router.post("/analyze-resume")
async def analyze_resume(
    request: Request,
    file: UploadFile = File(...),
    job_description: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user)

):
    if not file.filename.endswith((".pdf", ".docx", ".doc")):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX or DOC files are allowed")

    file_bytes = await file.read()

    if await request.is_disconnected():
        raise HTTPException(status_code=499, detail="Client disconnected during upload")

    if file.filename.endswith(".pdf"):
        pdf_bytes = file_bytes
    else:
        pdf_bytes = convert_doc_bytes_to_pdf_bytes(file_bytes, suffix=os.path.splitext(file.filename)[1])

    if await request.is_disconnected():
        raise HTTPException(status_code=499, detail="Client disconnected before processing")

    image_bytes_list = convert_pdf_to_image_bytes(pdf_bytes)

    if await request.is_disconnected():
        raise HTTPException(status_code=499, detail="Client disconnected before GPT processing")

    # Call the combined analysis function here
    # make sure this import matches your structure

    analysis_result = analyze_resume_from_images(image_bytes_list, job_description)

    if "error" in analysis_result:
        raise HTTPException(status_code=500, detail=f"LLM analysis error: {analysis_result['error']}")

    return analysis_result
