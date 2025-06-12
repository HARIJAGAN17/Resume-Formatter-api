import fitz 
from typing import List, Dict

def extract_links_from_pdf(pdf_bytes: bytes) -> List[Dict]:
    """
    Extracts hyperlinks from PDF bytes using PyMuPDF.
    
    Args:
        pdf_bytes (bytes): The PDF file content in bytes.
        
    Returns:
        List[Dict]: A list of hyperlinks with page number, bounding box text, and the URL.
    """
    links = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for page_num, page in enumerate(doc):
        for link in page.get_links():
            if "uri" in link:
                # Get the bounding box of the link
                rect = link["from"]
                try:
                    text = page.get_textbox(rect).strip()
                except Exception:
                    text = ""
                links.append({
                    "page": page_num + 1,
                    "text": text,
                    "uri": link["uri"]
                })

    return links