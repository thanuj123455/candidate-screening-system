import json
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import ResumeUploadResponse
from app.database import get_db
from app.services import upload_and_parse_resume

router = APIRouter(prefix="/resume", tags=["Resume"])

ALLOWED_CONTENT_TYPES = {"application/pdf"}
MAX_FILE_SIZE_MB = 10


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    name: str = Form(...),
    email: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File too large (max {MAX_FILE_SIZE_MB} MB).")

    # Reset file pointer so the service can read it again
    await file.seek(0)

    candidate = await upload_and_parse_resume(db, name, email, file)
    parsed = json.loads(candidate.parsed_resume or "{}")

    return ResumeUploadResponse(
        candidate_id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        parsed_data=parsed,
    )
