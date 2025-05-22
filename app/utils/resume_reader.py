import pdfplumber
from docx2pdf import convert
from typing import Union, Optional
from io import BytesIO
from docx import Document
import tempfile
import os
from pathlib import Path
import subprocess
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def _convert_to_pdf_with_libreoffice(doc_path: str) -> Optional[str]:
    try:
        output_dir = os.path.dirname(doc_path)
        base_name = Path(doc_path).stem

        process = subprocess.run([
            'soffice',
            '--headless',
            '--convert-to',
            'pdf',
            '--outdir',
            output_dir,
            doc_path
        ], capture_output=True, text=True, timeout=60)

        if process.returncode != 0:
            logger.warning(f"LibreOffice conversion failed: {process.stderr}")
            return None

        pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
        if os.path.exists(pdf_path):
            return pdf_path
        return None
    except Exception as e:
        logger.warning(f"LibreOffice conversion exception: {str(e)}")
        return None

def convert_doc_bytes_to_pdf_bytes(file_bytes: bytes, suffix=".docx") -> bytes:
    # Save DOC/DOCX to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_doc:
        temp_doc.write(file_bytes)
        temp_doc_path = temp_doc.name

    pdf_path = str(Path(temp_doc_path).with_suffix(".pdf"))
    try:
        # Try docx2pdf first (works only if Word installed, Windows/Mac)
        convert(temp_doc_path, pdf_path)
        if not os.path.exists(pdf_path):
            raise RuntimeError("docx2pdf did not produce output PDF.")
    except Exception as e:
        logger.warning(f"docx2pdf conversion failed: {e}. Trying LibreOffice fallback...")
        # Fallback to LibreOffice conversion
        pdf_path = _convert_to_pdf_with_libreoffice(temp_doc_path)
        if not pdf_path or not os.path.exists(pdf_path):
            os.remove(temp_doc_path)
            raise RuntimeError("Both docx2pdf and LibreOffice conversions failed.")

    # Read PDF bytes
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Cleanup
    os.remove(temp_doc_path)
    os.remove(pdf_path)

    return pdf_bytes

def extract_resume_text(file_bytes: bytes, filename: str) -> Union[str, None]:
    filename = filename.lower()
    try:
        if filename.endswith(".pdf"):
            return extract_text_from_pdf_bytes(file_bytes)

        elif filename.endswith(".docx"):
            pdf_bytes = convert_doc_bytes_to_pdf_bytes(file_bytes, suffix=".docx")
            return extract_text_from_pdf_bytes(pdf_bytes)

        elif filename.endswith(".doc"):
            pdf_bytes = convert_doc_bytes_to_pdf_bytes(file_bytes, suffix=".doc")
            return extract_text_from_pdf_bytes(pdf_bytes)

        else:
            logger.error(f"Unsupported file extension for extraction: {filename}")
            return None

    except Exception as e:
        logger.error(f"Error extracting resume text: {e}")
        # fallback to simple DOCX extraction for docx files only
        if filename.endswith(".docx"):
            return extract_text_from_docx(file_bytes)
        return None

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)
