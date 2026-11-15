import os
import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.core.config import settings
from backend.app.core.database import engine, Base, get_db
from backend.app.models import entities  # Ensure models are imported for metadata
from backend.app.services.graph.models import LegalEntityModel, LegalRelationshipModel
from backend.app.api.v1 import api_v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables & storage dirs exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.PROCESSED_DATA_DIR, exist_ok=True)
    os.makedirs("./data/qdrant_db", exist_ok=True)

    Base.metadata.create_all(bind=engine)
    print("[NyayaSaathi AI] Application tables initialized.")
    yield
    print("[NyayaSaathi AI] Application shutdown.")

app = FastAPI(
    title="NyayaSaathi AI (न्यायसाथी AI)",
    description="Official Full-Stack Indian Consumer Protection Legal Assistant & Grievance Resolution Platform.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 Routers
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/", tags=["System"])
def root():
    return {
        "project": "NyayaSaathi AI (न्यायसाथी AI)",
        "version": "1.0.0",
        "description": "Production RAG & Legal Knowledge Graph Platform for Indian Consumer Rights",
        "docs_url": "/docs",
        "health_url": "/health",
        "api_v1_prefix": "/api/v1",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "service": "NyayaSaathi AI",
        "version": "1.0.0"
    }

@app.get("/ready", tags=["System"])
def readiness_check(db: Session = Depends(get_db)):
    db_healthy = False
    try:
        db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception as e:
        db_error = str(e)

    return {
        "status": "ready" if db_healthy else "degraded",
        "database_connected": db_healthy,
        "environment": settings.APP_ENV,
        "embedding_model": settings.EMBEDDING_MODEL,
        "llm_primary_provider": settings.LLM_PRIMARY_PROVIDER,
        "llm_fallback_provider": settings.LLM_FALLBACK_PROVIDER,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
