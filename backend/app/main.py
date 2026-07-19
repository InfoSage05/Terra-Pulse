from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from backend.app.core.config import settings
from backend.app.core.security import get_api_key
from backend.app.middleware.rate_limit import limiter
from backend.app.middleware.request_logging import RequestLoggingMiddleware
from backend.app.api import health
from backend.app.api.v1 import areas, scores, predict, properties, neighborhoods

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)

api_router = APIRouter(dependencies=[Depends(get_api_key)])
api_router.include_router(areas.router, prefix="/areas", tags=["areas"])
api_router.include_router(scores.router, prefix="/areas", tags=["scores"])
api_router.include_router(predict.router, prefix="/predict", tags=["predict"])
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(neighborhoods.router, prefix="/neighborhoods", tags=["neighborhoods"])

app.include_router(api_router, prefix=settings.API_V1_STR)
