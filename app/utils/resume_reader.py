import pdfplumber
from docx2pdf import convert
from typing import List, Union, Optional
from io import BytesIO
from docx import Document
import tempfile
import os
from pathlib import Path
import subprocess
import logging
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
from datetime import datetime
import aspose.words as aw

logger = logging.getLogger(__name__)


# codes commented out were related to text extraction from the documents

# def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
#     with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
#         return "\n".join(page.extract_text() or "" for page in pdf.pages)

def convert_doc_bytes_to_pdf_bytes(file_bytes: bytes, suffix=".docx") -> bytes:
    # Save the DOC/DOCX to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_doc:
        temp_doc.write(file_bytes)
        temp_doc_path = temp_doc.name

    # Define output PDF path
    pdf_path = str(Path(temp_doc_path).with_suffix(".pdf"))

    try:
        # Load and convert with Aspose
        doc = aw.Document(temp_doc_path)
        doc.save(pdf_path, aw.SaveFormat.PDF)

        # Read PDF bytes
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

    finally:
        # Cleanup
        if os.path.exists(temp_doc_path):
            os.remove(temp_doc_path)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    return pdf_bytes

# def extract_resume_text(file_bytes: bytes, filename: str) -> Union[str, None]:
#     filename = filename.lower()
#     try:
#         if filename.endswith(".pdf"):
#             return extract_text_from_pdf_bytes(file_bytes)

#         elif filename.endswith(".docx"):
#             pdf_bytes = convert_doc_bytes_to_pdf_bytes(file_bytes, suffix=".docx")
#             return extract_text_from_pdf_bytes(pdf_bytes)

#         elif filename.endswith(".doc"):
#             pdf_bytes = convert_doc_bytes_to_pdf_bytes(file_bytes, suffix=".doc")
#             return extract_text_from_pdf_bytes(pdf_bytes)

#         else:
#             logger.error(f"Unsupported file extension for extraction: {filename}")
#             return None

#     except Exception as e:
#         logger.error(f"Error extracting resume text: {e}")
#         # fallback to simple DOCX extraction for docx files only
#         if filename.endswith(".docx"):
#             return extract_text_from_docx(file_bytes)
#         return None

# def extract_text_from_docx(file_bytes: bytes) -> str:
#     doc = Document(BytesIO(file_bytes))
#     return "\n".join(p.text for p in doc.paragraphs)



def convert_pdf_to_image_bytes(pdf_bytes: bytes) -> List[bytes]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []

    for page in doc:
        pix = page.get_pixmap(dpi=300, alpha=False)
        img_bytes = pix.tobytes("png")

        # Open as PIL image and crop headers/footers (optional)
        image = Image.open(BytesIO(img_bytes))
        cropped = image.crop((0, 50, image.width, image.height - 50))  # Adjust crop values if needed

        # Save cropped image to bytes (without saving to disk)
        output = BytesIO()
        cropped.save(output, format="PNG")
        images.append(output.getvalue())

    return images