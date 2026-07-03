from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

def rate_limit_exceeded_handler(request, exc: RateLimitExceeded):
    return _rate_limit_exceeded_handler(request, exc)
