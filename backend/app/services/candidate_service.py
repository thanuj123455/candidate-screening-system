from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Candidate
from app.resume_parser import parse_resume
from app.utils.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)

_UPLOAD_DIR = Path(settings.upload_dir)


async def upload_and_parse_resume(
    db: AsyncSession,
    name: str,
    email: str,
    filename: str | None,
    file_contents: bytes,
) -> Candidate:
    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = f"{email.replace('@', '_').replace('.', '_')}_{filename or 'upload.pdf'}"
    dest = _UPLOAD_DIR / safe_name
    dest.write_bytes(file_contents)

    parsed = await parse_resume(dest)

    # Upsert candidate (re-upload updates resume)
    result = await db.execute(select(Candidate).where(Candidate.email == email))
    candidate = result.scalar_one_or_none()

    if candidate:
        candidate.resume_path = str(dest)
        candidate.parsed_resume = parsed.model_dump_json()
    else:
        candidate = Candidate(
            name=name,
            email=email,
            resume_path=str(dest),
            parsed_resume=parsed.model_dump_json(),
        )
        db.add(candidate)

    await db.flush()
    await db.refresh(candidate)
    log.info(f"Candidate created/updated: {candidate.id}")
    return candidate


async def get_candidate(db: AsyncSession, candidate_id: UUID) -> Candidate | None:
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    return result.scalar_one_or_none()
