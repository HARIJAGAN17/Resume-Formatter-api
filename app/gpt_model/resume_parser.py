import base64
from typing import List
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
from fastapi import HTTPException


llm = AzureChatOpenAI(
    azure_deployment="gpt4o",
    api_version="2024-10-21",
)

def extract_resume_data_from_image(image_bytes_list: List[bytes]) -> dict:
    # Convert image bytes to base64 data URIs
    image_content_list = []
    for img_bytes in image_bytes_list:
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        image_content_list.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{b64}"
            }
        })

    prompt = [
        SystemMessage(content="You are an assistant that extracts structured resume data in a clean JSON format for backend use."),
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": """You are an assistant that extracts all useful resume data from full-page images, including headers and footers. Logos or text in the header/footer may contain important values like certification,skills or job title information and return in this exact JSON format:

{
  "name": "<candidate_full_name>",
  "summary": ["<bullet_point_summary_1>", "..."],
  "education": [{"degree": "<degree>",
      "university": "<university>"}],
  "technicalExpertise": {
    "<category_1>": ["<item_1>", "<item_2>", "..."],
    "<category_2>": ["<item_1>", "..."],
    "...": "..."
  },
  "certifications": ["<certification_1>", "..."],
  "experience": [
    {
      "company": "<company_name>",
      "date": "<duration>",
      "role": "<job_title>",
      "clientEngagement": "<client_name_or_empty_string>",
      "program": "<program_name_or_empty_string>",
      "responsibilities": ["<responsibility_1>", "...or empty array if not available"]
    }
  ],
  "contact": {
  "email": "<email_or_empty>",
  "phone": "<phone_or_empty>",
  "linkedin": "<linkedin_url_or_empty>",
  "github": "<github_url_or_empty>",
  "portfolio": "<portfolio_url_or_empty>"
    },
  "externalLinks": ["<url_1>", "<url_2>", "..."]

}

Guidelines:
- Analyze the **entire page**, including **headers, footers, and logos**.
- Useful details may appear in **header/footer regions**, such as company names, job roles, logos, or page-wide banners — extract these if relevant like example if certificate it should be certificate not any other irrelevant information.
- Under "technicalExpertise", intelligently group technologies and tools into meaningful categories (e.g., Programming Languages, Frameworks, DevOps & Cloud, Databases, BPM Tools, etc.).
- Do NOT use fixed or predefined categories — infer them based on the resume.
- In "summary", extract all relevant overview points from sections like "Profile Summary", "Professional Summary", "Professional Experience", etc.
- If the total combined character length of all summary bullet points exceeds 1400 characters, **rephrase and shorten** the summary to highlight only the **most important strengths and roles**, and ensure it is **within 1400 characters total**.
- Include every company listed under experience, even if that entry has no detailed responsibilities. Leave such fields empty or as empty arrays.
- Always return valid JSON — no markdown or explanation.
- Extract **all URLs** from the resume, including:
- Contact URLs (LinkedIn, GitHub, portfolio, etc.),
- Additional links (blogs, articles, Notion, published documents, certificates, etc.)
- Include *every* valid URL under the `"externalLinks"` array — even if it is already present under the `"contact"` section. Do not filter or deduplicate across sections.
- Return all top-level keys, even if values are empty arrays or empty strings.
- Resume may list **multiple roles within the same company** (e.g., Cognizant) — extract each role as a **separate experience entry**, keeping the same company name.
"""
                }
            ] + image_content_list
        )
    ]

    response = llm.invoke(prompt)
    return {"response": response.content}



llm = AzureChatOpenAI(
    azure_deployment="gpt4o",
    api_version="2024-10-21",
)

def analyze_resume_from_images(image_bytes_list: List[bytes], job_description: str) -> dict:
    # Convert image bytes to base64 data URIs
    image_content_list = []
    for img_bytes in image_bytes_list:
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        image_content_list.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{b64}"
            }
        })

    # Compose prompt
    prompt = [
        SystemMessage(content="You are an expert career coach and resume analyst."),
        HumanMessage(content=[
            {
                "type": "text",
                "text": f"""
Analyze the resume image(s) and compare it to the job description provided. Your goal is to assess how suitable the candidate is for the job, even if they are overqualified.

Instructions:
- If the candidate is **overqualified** or **has more experience than needed**, they should still receive a **high score** if relevant skills and roles align.
- When evaluating experience, carefully check if the candidate's experience is **relevant to the job requirements**. For example, if the job requires 4+ years of experience in ASP.NET, verify if the candidate has at least 4 years working directly with ASP.NET or closely related technologies/roles (e.g., full-stack development with significant ASP.NET use).
- Experience in general software engineering or unrelated roles should be weighted less if it does not align with the core job requirements.
- Consider soft skills, certifications, and evidence of adaptability if shown in the resume.
- Provide clear reasoning on experience relevance and its impact on the score.

Return your response as a valid JSON object in this format:

{{
  "summary": [
    "<key_strength_point_1>",
    "<key_strength_point_2>",
    "<key_strength_point_3>",
    "<key_strength_point_4>",
    "<key_strength_point_5>"
  ],
  "compatibility_score": {{
    "technical_skills": "<percent>%",
    "experience_level": "<percent>%",
    "education": "<percent>%",
    "keywords_match": "<percent>%"
  }},
  "job_score": "<overall_match_percent>%",
  "job_score_reasoning": {{
  "overall": "<reasoning text>",
  "overall_improvement": "<improvement text>",
  "technical_skills": "<reasoning text>",
  "technical_skills_improvement": "<improvement text>",
  "experience_level": "<reasoning text>",
  "experience_level_improvement": "<improvement text>",
  "education": "<reasoning text>",
  "education_improvement": "<improvement text>",
  "keywords_match": "<reasoning text>",
  "keywords_match_improvement": "<improvement text>"
}}
}}

Job Description:
\"\"\"{job_description}\"\"\"
"""
            }
        ] + image_content_list)
    ]

    # Invoke LLM
    response = llm.invoke(prompt)

    raw_response = response.content
    cleaned = raw_response.strip().strip("`")
    if cleaned.lower().startswith("json"):
        cleaned = cleaned[4:].strip()

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("LLM JSON Decode Error:", e)
        print("Raw LLM Output:", raw_response)
        raise HTTPException(status_code=500, detail="LLM analysis error: Failed to parse LLM response as JSON.")

    return result
