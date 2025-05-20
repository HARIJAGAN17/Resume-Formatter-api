import json
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.utils.resume_reader import extract_resume_text
from app.gpt_model.resume_parser import extract_resume_data
from app.authentication.auth import get_current_user
from app.model.user_auth import User
import tiktoken

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
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX files are allowed")

    file_bytes = await file.read()
    text = extract_resume_text(file_bytes, file.filename)

    if not text:
        raise HTTPException(status_code=400, detail="Failed to extract resume text")

    token_count = count_tokens(text)
    print(f"Token count for extracted resume text: {token_count}")

    gpt_response = extract_resume_data(text)
    gpt_text = gpt_response.get("response", "")

    cleaned = gpt_text.strip("`").strip()
    if cleaned.startswith("json"):
        cleaned = cleaned[len("json"):].strip()

    try:
        structured_data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("JSON Error:", e)
        raise HTTPException(status_code=500, detail="Invalid JSON from GPT response")

    # 🔽 Sort experience based on completeness score
    if "experience" in structured_data:
        structured_data["experience"].sort(key=experience_completeness_score, reverse=True)

    return structured_data
