import logging
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery
from src.core.engine import VisionFlowEngine
from src.stream.manager import StreamManager
from src.config.settings import Settings

logger = logging.getLogger(__name__)

# --- Security ---
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)

async def get_api_key(
    header: str = Security(api_key_header),
    query: str = Security(api_key_query),
):
    if header == Settings.API_KEY or query == Settings.API_KEY:
        return header or query
    raise HTTPException(status_code=403, detail="Could not validate credentials")

# --- Singletons ---
_engine = None
_stream_manager = None

def get_engine() -> VisionFlowEngine:
    global _engine
    if _engine is None:
        logger.info("Init Engine singleton...")
        _engine = VisionFlowEngine()
    return _engine

def get_stream_manager() -> StreamManager:
    global _stream_manager
    if _stream_manager is None:
        logger.info("Init Stream Manager singleton...")
        _stream_manager = StreamManager()
    return _stream_manager
