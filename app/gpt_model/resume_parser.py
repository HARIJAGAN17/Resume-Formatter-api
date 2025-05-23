import base64
from typing import List
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


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
  ]
}

Guidelines:
- Analyze the **entire page**, including **headers, footers, and logos**.
- Useful details may appear in **header/footer regions**, such as company names, job roles, logos, or page-wide banners — extract these if relevant like example if certificate it should be certificate not any other irrelevant information.
- Under "technicalExpertise", intelligently group technologies and tools into meaningful categories (e.g., Programming Languages, Frameworks, DevOps & Cloud, Databases, BPM Tools, etc.).
- Do NOT use fixed or predefined categories — infer them based on the resume.
- In "summary", extract all relevant overview points from sections like "Profile Summary", "Professional Summary", "Professional Experience", etc.
- Include every company listed under experience, even if that entry has no detailed responsibilities. Leave such fields empty or as empty arrays.
- Always return valid JSON — no markdown or explanation.
- Return all top-level keys, even if values are empty arrays or empty strings.
- Resume may list **multiple roles within the same company** (e.g., Cognizant) — extract each role as a **separate experience entry**, keeping the same company name.
"""
                }
            ] + image_content_list
        )
    ]

    response = llm.invoke(prompt)
    return {"response": response.content}
