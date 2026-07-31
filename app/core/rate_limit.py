import time
from collections import defaultdict
from threading import Lock
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.config import settings

_rate_limit_store = defaultdict(list)
_store_lock = Lock()

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = 60

        with _store_lock:
            requests = _rate_limit_store[client_ip]
            requests[:] = [t for t in requests if now - t < window]

            if len(requests) >= settings.RATE_LIMIT_PER_MINUTE:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please try again later."}
                )

            requests.append(now)

        return await call_next(request)
