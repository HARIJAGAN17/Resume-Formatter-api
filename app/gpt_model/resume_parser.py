from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

llm = AzureChatOpenAI(
    azure_deployment="gpt4o",
    api_version="2024-10-21",
)

def extract_resume_data(text: str) -> dict:
    prompt = [
        ("system", "You are an assistant that extracts structured resume data in a clean JSON format for backend use."),
        HumanMessage(
            content=f"""
Extract the following details from the resume text and return in this exact JSON format:

{{
  "name": "<candidate_full_name>",
  "summary": ["<bullet_point_summary_1>", "..."],
  "education": {{
    "degree": "<degree>",
    "university": "<university>"
  }},
  "technicalExpertise": {{
    "<category_1>": ["<item_1>", "<item_2>", "..."],
    "<category_2>": ["<item_1>", "..."],
    "...": "..."
  }},
  "certifications": ["<certification_1>", "..."],
  "experience": [
    {{
      "company": "<company_name>",
      "date": "<duration>",
      "role": "<job_title>",
      "clientEngagement": "<client_name_or_empty_string>",
      "program": "<program_name_or_empty_string>",
      "responsibilities": ["<responsibility_1>", "...or empty array if not available"]
    }},
    ...
  ]
}}

Guidelines:
- Under "technicalExpertise", intelligently group technologies and tools into meaningful categories (e.g., Programming Languages, Frameworks, DevOps & Cloud, Databases, BPM Tools, etc.).
- Do NOT use fixed or predefined categories — infer them based on the resume.
- In "summary", extract all relevant overview points from sections like "Profile Summary", "Professional Summary","Professional Experience",etc.
- Include every company listed under experience, even if that entry has no detailed responsibilities. Leave such fields empty or as empty arrays.
- Always return valid JSON — no markdown or explanation.
- Return all top-level keys, even if values are empty arrays or empty strings.
- Resume text follows below.
- Resume may list **multiple roles within the same company** (e.g., Cognizant) — extract each role as a **separate experience entry**, keeping the same company name.

Resume Text:
{text}
"""
        )
    ]

    response = llm.invoke(prompt)
    return {"response": response.content}
    