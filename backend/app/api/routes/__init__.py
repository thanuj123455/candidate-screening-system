from fastapi import APIRouter
from .resume import router as resume_router
from .interview import router as interview_router
from .report import router as report_router

api_router = APIRouter()
api_router.include_router(resume_router)
api_router.include_router(interview_router)
api_router.include_router(report_router)
