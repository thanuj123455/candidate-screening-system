import json
import re

from openai import AsyncOpenAI

from app.interview.prompts import REPORT_GENERATION_PROMPT
from app.resume_parser.schemas import ParsedResume
from app.utils.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)


async def generate_report(
    role: str,
    resume: ParsedResume,
    qa_pairs: list[dict],  # [{"question": str, "answer": str}]
) -> dict:
    transcript = "\n\n".join(
        f"Q{i+1}: {pair['question']}\nA: {pair['answer']}"
        for i, pair in enumerate(qa_pairs)
    )
    prompt = REPORT_GENERATION_PROMPT.format(
        role=role,
        resume_summary=resume.to_summary(),
        transcript=transcript,
    )

    client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    message = await client.chat.completions.create(
        model=settings.llm_model,
        max_tokens=settings.llm_max_tokens,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        log.error(f"Report JSON parse failed: {e}\nRaw: {raw[:200]}")
        return {
            "summary": raw,
            "strengths": [],
            "weaknesses": [],
            "overall_score": None,
            "recommendation": "Maybe",
            "per_question_scores": [],
        }
