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
      "clientEngagement": "<client_name>",
      "program": "<program_name>",
      "responsibilities": ["<responsibility_1>", "..."]
    }}
  ]
}}

Guidelines:
- Under "technicalExpertise", intelligently group technologies and tools into meaningful categories (e.g., Programming Languages, Frameworks, DevOps & Cloud, Databases, BPM Tools, etc.).
- Do NOT use fixed or predefined categories — infer them based on the content of the resume.
- In "summary", extract **all relevant overview points** from sections like "Profile Summary", "Professional Summary", or other introductory paragraphs. Include all non-redundant bullet points even if phrased similarly across sections.
- Return only valid JSON — no markdown or explanation.
- Format all arrays clearly.
- Always include all top-level keys in the JSON, even if their values are empty strings, empty arrays, or null.
- Resume text follows below.

Resume Text:
{text}
"""
    )
]


    response = llm.invoke(prompt)
    return {"response": response.content}

