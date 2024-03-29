import os

from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

def init_limiter(app: FastAPI):
    limiter = Limiter(key_func=get_remote_address, storage_uri=f"{os.getenv('REDIS_CONNECTION', 'redis://redis')}\n")
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
