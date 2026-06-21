"""
InterviewGPT — Resume Parser (PDF & DOCX)

Extracts raw text from uploaded resume files using:
- PyPDF2 + pdfplumber for PDFs
- python-docx for DOCX files
"""

import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file using pdfplumber (better layout handling)."""
    text_parts = []
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception as e:
        logger.warning(f"pdfplumber failed, falling back to PyPDF2: {e}")
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        except Exception as e2:
            logger.error(f"Both PDF parsers failed: {e2}")
            raise ValueError("Could not extract text from PDF file")

    return "\n\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n\n".join(paragraphs)
    except Exception as e:
        logger.error(f"DOCX parsing failed: {e}")
        raise ValueError("Could not extract text from DOCX file")


def extract_text(file_bytes: bytes, file_type: str) -> str:
    """Extract text from a resume file based on its type."""
    if file_type == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif file_type == "docx":
        return extract_text_from_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


async def parse_resume_with_ai(raw_text: str) -> dict:
    """
    Use LLM to extract structured data from resume text.
    Returns: { name, skills, education, experience, projects, certifications }
    """
    from backend.llm.agent import get_llm
    import json

    llm = get_llm()
    if llm.__class__.__name__ == "MockLLM":
        return _basic_extraction(raw_text)

    prompt = f"""Extract structured information from this resume text. 
Return ONLY a valid JSON object with these exact keys:

{{
    "name": "Full name of the candidate",
    "skills": ["skill1", "skill2", ...],
    "education": [
        {{"degree": "...", "institution": "...", "year": "...", "gpa": "..."}}
    ],
    "experience": [
        {{"title": "...", "company": "...", "duration": "...", "description": "..."}}
    ],
    "projects": [
        {{"name": "...", "description": "...", "technologies": ["..."]}}
    ],
    "certifications": ["cert1", "cert2", ...]
}}

Resume text:
{raw_text}

Return ONLY the JSON, no markdown formatting or code blocks."""

    try:
        response = await llm.ainvoke(prompt)
        content = response.content.strip()
        # Clean up any markdown formatting
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            content = content.rsplit("```", 1)[0]
        return json.loads(content)
    except Exception as e:
        logger.error(f"AI resume parsing failed: {e}")
        return _basic_extraction(raw_text)


def _basic_extraction(raw_text: str) -> dict:
    """Fallback basic extraction without AI."""
    lines = raw_text.strip().split("\n")
    return {
        "name": lines[0] if lines else "Unknown",
        "skills": [],
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
    }
