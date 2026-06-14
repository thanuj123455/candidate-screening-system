import re
import json
from pathlib import Path

import anthropic
import pdfplumber

from app.resume_parser.schemas import ParsedResume
from app.utils.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)

_EXTRACTION_PROMPT = """
You are a resume parser. Extract structured information from the following resume text.
Return ONLY valid JSON matching this schema (no markdown, no extra text):

{
  "name": "string",
  "email": "string",
  "phone": "string",
  "skills": ["list of general skills"],
  "programming_languages": ["Python", "Java", ...],
  "frameworks": ["FastAPI", "React", ...],
  "tools": ["Docker", "Git", ...],
  "projects": ["Project title: brief description", ...],
  "experience": ["Role at Company (year–year): summary", ...],
  "education": "Degree, Institution, Year",
  "certifications": ["Cert name", ...]
}

Resume text:
\"\"\"
{resume_text}
\"\"\"
"""


def extract_text_from_pdf(path: str | Path) -> str:
    text_parts: list[str] = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    return "\n".join(text_parts)


async def parse_resume(path: str | Path) -> ParsedResume:
    raw_text = extract_text_from_pdf(path)
    if not raw_text.strip():
        log.warning("PDF yielded no text; returning empty resume")
        return ParsedResume(raw_text=raw_text)

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    prompt = _EXTRACTION_PROMPT.format(resume_text=raw_text[:8000])  # stay within context

    try:
        message = await client.messages.create(
            model=settings.llm_model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_json = message.content[0].text.strip()
        # Strip markdown code fences if model adds them
        raw_json = re.sub(r"^```(?:json)?\s*", "", raw_json)
        raw_json = re.sub(r"\s*```$", "", raw_json)
        data = json.loads(raw_json)
        return ParsedResume(**data, raw_text=raw_text)
    except Exception as e:
        log.error(f"LLM resume extraction failed: {e}")
        # Fallback: return raw text only
        return ParsedResume(raw_text=raw_text)
