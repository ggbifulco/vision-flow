import hmac
import logging
import threading

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config.settings import Settings
from src.core.engine import VisionFlowEngine
from src.stream.manager import StreamManager

logger = logging.getLogger(__name__)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)

# --- Rate Limiter (shared) ---
limiter = Limiter(key_func=get_remote_address)


async def get_api_key(
    header: str = Security(api_key_header),
    query: str = Security(api_key_query),
) -> str:
    key = header or query
    if key and hmac.compare_digest(key, Settings.API_KEY):
        return key
    raise HTTPException(status_code=403, detail="Could not validate credentials")


# --- Singletons (thread-safe) ---
_engine = None
_stream_manager = None
_lock = threading.Lock()


def get_engine() -> VisionFlowEngine:
    global _engine
    if _engine is None:
        with _lock:
            if _engine is None:
                logger.info("Init Engine singleton...")
                _engine = VisionFlowEngine()
    return _engine


def get_stream_manager() -> StreamManager:
    global _stream_manager
    if _stream_manager is None:
        with _lock:
            if _stream_manager is None:
                logger.info("Init Stream Manager singleton...")
                _stream_manager = StreamManager()
    return _stream_manager
