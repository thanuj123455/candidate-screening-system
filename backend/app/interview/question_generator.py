from openai import AsyncOpenAI

from app.interview.prompts import QUESTION_GENERATION_PROMPT, FOLLOW_UP_PROMPT
from app.resume_parser.schemas import ParsedResume
from app.utils.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)

_DIFFICULTY_SEQUENCE = ["easy", "medium", "medium", "hard", "hard", "hard", "medium", "hard"]


async def generate_question(
    role: str,
    resume: ParsedResume,
    context_chunks: list[str],
    asked_questions: list[str],
    question_index: int,
) -> tuple[str, str]:
    """
    Returns (question_text, source_context).
    source_context is the joined RAG chunks used.
    """
    difficulty = _DIFFICULTY_SEQUENCE[min(question_index, len(_DIFFICULTY_SEQUENCE) - 1)]
    context = "\n\n---\n\n".join(context_chunks)
    asked_str = "\n".join(f"- {q}" for q in asked_questions) if asked_questions else "None"

    prompt = QUESTION_GENERATION_PROMPT.format(
        role=role,
        resume_summary=resume.to_summary(),
        context=context[:4000],
        asked_questions=asked_str,
        difficulty=difficulty,
    )

    client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    message = await client.chat.completions.create(
        model=settings.llm_model,
        max_tokens=512,
        temperature=settings.llm_temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    question_text = message.choices[0].message.content.strip()
    log.info(f"Generated question [{difficulty}]: {question_text[:80]}...")
    return question_text, context[:2000]


async def generate_follow_up(original_question: str, candidate_answer: str) -> str:
    prompt = FOLLOW_UP_PROMPT.format(
        original_question=original_question,
        candidate_answer=candidate_answer,
    )
    client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    message = await client.chat.completions.create(
        model=settings.llm_model,
        max_tokens=256,
        temperature=0.5,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.choices[0].message.content.strip()
