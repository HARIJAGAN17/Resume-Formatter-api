import pdfplumber
from docx2pdf import convert
from typing import Union
from io import BytesIO
from docx import Document
import tempfile
import os
from pathlib import Path

def extract_text_from_pdf(file_bytes: bytes) -> str:
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def convert_docx_bytes_to_pdf_bytes(file_bytes: bytes) -> bytes:
    # Save DOCX to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
        temp_docx.write(file_bytes)
        temp_docx_path = temp_docx.name

    pdf_path = str(Path(temp_docx_path).with_suffix(".pdf"))

    # Convert DOCX to PDF using Word
    convert(temp_docx_path, pdf_path)

    # Read the converted PDF
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Cleanup
    os.remove(temp_docx_path)
    os.remove(pdf_path)

    return pdf_bytes

def extract_resume_text(file_bytes: bytes, filename: str) -> Union[str, None]:
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename.endswith(".docx"):
        try:
            # Convert DOCX → PDF → Extract text
            pdf_bytes = convert_docx_bytes_to_pdf_bytes(file_bytes)
            return extract_text_from_pdf(pdf_bytes)
        except Exception as e:
            print("DOCX to PDF conversion failed:", e)
            return extract_text_from_docx(file_bytes)  # fallback to regular .docx reading
    return None

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)
