from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.areas import router as areas_router

from app.db.database import Base, engine
from app.api.auth import router as auth_router
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TerraPulse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # must be exact origin, not "*", for cookies to work
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(areas_router)

@app.get("/health")
def health():
    return {"status": "ok"}