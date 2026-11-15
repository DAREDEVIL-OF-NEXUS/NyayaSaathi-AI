from fastapi import APIRouter
from .auth import router as auth_router
from .chat import router as chat_router
from .complaints import router as complaints_router
from .documents import router as documents_router
from .knowledge import router as knowledge_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(chat_router, tags=["Chat & Consultation"])
api_v1_router.include_router(complaints_router, tags=["Consumer Complaints"])
api_v1_router.include_router(documents_router, tags=["Document Ingestion & Analysis"])
api_v1_router.include_router(knowledge_router, tags=["Knowledge Base & Graph"])

__all__ = ["api_v1_router"]
