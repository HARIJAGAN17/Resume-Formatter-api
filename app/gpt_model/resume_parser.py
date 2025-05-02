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
        ("system", "You are an assistant that extracts structured resume data."),
        HumanMessage(
            content=f"""
Extract the following details from the resume text:
- Name
- Email
- Phone Number
- Education (school, degree, years)
- Work Experience (company, title, duration, responsibilities)
- Skills
- if other section are available extract them also like above fields

Respond in a structured JSON format.

Resume text:
{text}
"""
        )
    ]

    response = llm.invoke(prompt)
    return response.content
