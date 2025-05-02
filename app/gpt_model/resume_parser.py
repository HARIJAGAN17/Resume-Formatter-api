from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

llm = AzureChatOpenAI(
    azure_deployment="gpt4o",
    api_version="2024-10-21",
)

def extract_resume_data(text: str) -> str:
    # Constructing the prompt with the extracted resume text
    prompt = [
        ("system", "You are an assistant that extracts structured resume data. The response must be a valid JSON object with clear key-value pairs."),
        HumanMessage(
            content=f"""
Extract the following details from the resume text:
- Name
- Email
- Phone Number
- Location
- LinkedIn (if available)
- GitHub (if available)
- Profile Summary (optional)
- Education (school, degree, years, CGPA, if available)
- Work Experience (company, title, duration, responsibilities)
- Skills (including technical skills, frameworks, databases, soft skills)
- Achievements (if available)
- Certifications (if available)
- Academic Projects (project names and descriptions)
- Links (any other relevant links)

Return the data in the following format:

{{
  "Name": "<name>",
  "Email": "<email>",
  "Phone Number": "<phone_number>",
  "Location": "<location>",
  "LinkedIn": "<linkedin_url>",
  "GitHub": "<github_url>",
  "Profile Summary": "<profile_summary>",
  "Education": {{
    "School": "<school_name>",
    "Degree": "<degree>",
    "Years": "<years>",
    "CGPA": "<cgpa>"
  }},
  "Skills": {{
    "Technical Skills": ["<skill_1>", "<skill_2>", ...],
    "Frameworks/Libraries": ["<framework_1>", "<framework_2>", ...],
    "Databases": ["<database_1>", "<database_2>", ...],
    "Soft Skills": ["<soft_skill_1>", "<soft_skill_2>", ...],
    "Interests": ["<interest_1>", "<interest_2>", ...]
  }},
  "Work Experience": [
    {{
      "Company": "<company_name>",
      "Title": "<job_title>",
      "Duration": "<job_duration>",
      "Responsibilities": ["<responsibility_1>", "<responsibility_2>", ...]
    }}
  ],
  "Achievements": ["<achievement_1>", "<achievement_2>", ...],
  "Certifications": ["<certification_1>", "<certification_2>", ...],
  "Academic Projects": [
    {{
      "Name": "<project_name>",
      "Description": "<project_description>"
    }}
  ],
  "Links": {{
    "LinkedIn": "<linkedin_url>",
    "GitHub": "<github_url>",
    "Other": ["<other_link_1>", "<other_link_2>"]
  }}
}}

# Pass the resume text here for extraction
Resume text:
{text}  # This is where the resume content is inserted into the prompt
"""
        )
    ]

    response = llm.invoke(prompt)
    return {"response": response.content  }
