"""
InterviewGPT — Resume Text Chunking

Splits resume text into overlapping chunks for embedding storage.
Uses recursive character splitting for context preservation.
"""

from typing import List


def chunk_resume_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> List[dict]:
    """
    Split resume text into overlapping chunks with metadata.
    
    Returns list of dicts with 'text', 'index', 'section_hint' keys.
    """
    if not text or not text.strip():
        return []

    # Split by sections first (double newlines often indicate section breaks)
    sections = _split_into_sections(text)
    
    chunks = []
    chunk_index = 0

    for section_name, section_text in sections:
        # If section is small enough, keep it as one chunk
        if len(section_text) <= chunk_size:
            chunks.append({
                "text": section_text.strip(),
                "index": chunk_index,
                "section_hint": section_name,
            })
            chunk_index += 1
            continue

        # Recursive character splitting for larger sections
        start = 0
        while start < len(section_text):
            end = start + chunk_size
            
            # Try to break at a sentence boundary
            if end < len(section_text):
                # Look for sentence endings near the chunk boundary
                for sep in [". ", "\n", ", ", " "]:
                    last_sep = section_text.rfind(sep, start, end)
                    if last_sep > start + chunk_size // 2:
                        end = last_sep + len(sep)
                        break

            chunk_text = section_text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "index": chunk_index,
                    "section_hint": section_name,
                })
                chunk_index += 1

            start = end - chunk_overlap

    return chunks


def _split_into_sections(text: str) -> List[tuple]:
    """
    Attempt to identify resume sections by common headers.
    Returns (section_name, section_text) tuples.
    """
    section_keywords = [
        "education", "experience", "work experience", "projects",
        "skills", "technical skills", "certifications", "awards",
        "summary", "objective", "about", "contact", "publications",
        "achievements", "languages", "interests", "references",
    ]

    lines = text.split("\n")
    sections = []
    current_section = "header"
    current_lines = []

    for line in lines:
        line_lower = line.strip().lower().rstrip(":")
        if line_lower in section_keywords:
            if current_lines:
                sections.append((current_section, "\n".join(current_lines)))
            current_section = line_lower
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_section, "\n".join(current_lines)))

    if not sections:
        sections = [("full_resume", text)]

    return sections
