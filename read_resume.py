import io
from typing import Optional

import pdfplumber

try:
    from pdf2image import convert_from_bytes
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract raw text from PDF bytes using pdfplumber."""
    text_chunks = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_chunks.append(page_text)
    
    extracted_text = "\n".join(text_chunks).strip()
    
    if not extracted_text and OCR_AVAILABLE:
        try:
            images = convert_from_bytes(pdf_bytes)
            ocr_text = []
            for image in images:
                text = pytesseract.image_to_string(image)
                ocr_text.append(text)
            extracted_text = "\n".join(ocr_text).strip()
        except Exception:
            pass
            
    return extracted_text


def extract_text_from_uploaded_file(uploaded_file) -> str:
    """Extract text from a Streamlit uploaded file (PDF only)."""
    if uploaded_file is None:
        return ""

    filename = getattr(uploaded_file, "name", "")
    if not filename.lower().endswith(".pdf"):
        raise ValueError("Only PDF resumes are supported.")

    pdf_bytes = uploaded_file.read()
    if not pdf_bytes:
        return ""

    return extract_text_from_pdf(pdf_bytes)


def safe_extract_text(uploaded_file) -> Optional[str]:
    """Safe wrapper that returns None when extraction fails."""
    try:
        return extract_text_from_uploaded_file(uploaded_file)
    except Exception:
        return None
