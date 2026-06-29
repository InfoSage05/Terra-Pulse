import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.app.core.logging import logger

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        request_info = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency": round(process_time, 4),
            "api_key_id": "present" if request.headers.get("X-API-Key") else "missing"
        }
        
        logger.info("Handled request", extra={"request_info": request_info})
        return response
