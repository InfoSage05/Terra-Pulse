from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler


def rate_limit_key(request: Request) -> str:
    """Key by API key when present so rotating IPs can't bypass the limit
    by spreading requests across addresses; every real request already
    carries X-API-Key (see core/security.py), so this is the meaningful
    identity for rate limiting. Falls back to IP for unauthenticated
    requests (e.g. /health, /ready, or a request missing the header - which
    will be rejected by get_api_key anyway, but still needs *a* rate-limit
    key to avoid an unkeyed flood)."""
    api_key = request.headers.get("X-API-Key")
    return api_key if api_key else get_remote_address(request)


limiter = Limiter(key_func=rate_limit_key, default_limits=["100/minute"])

def rate_limit_exceeded_handler(request, exc: RateLimitExceeded):
    return _rate_limit_exceeded_handler(request, exc)
