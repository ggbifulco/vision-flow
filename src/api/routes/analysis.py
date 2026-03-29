import re
import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.api.deps import limiter, get_api_key, get_engine, get_stream_manager
from src.config.settings import Settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Analysis"])

_PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)", re.I),
    re.compile(r"you\s+are\s+now\s+(a|an|the)", re.I),
    re.compile(r"system\s*prompt", re.I),
    re.compile(r"reveal\s+(your|the)\s+(instructions|prompt|rules|system)", re.I),
    re.compile(r"forget\s+(everything|all|your)", re.I),
    re.compile(r"override\s+(safety|guardrails|rules)", re.I),
]


def _is_prompt_injection(text: str) -> bool:
    return any(p.search(text) for p in _PROMPT_INJECTION_PATTERNS)


class QueryRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)


@router.get("/latest_analysis")
async def get_latest_analysis(api_key: str = Depends(get_api_key)) -> dict:
    vfe = get_engine()
    return {
        "analysis": vfe.last_analysis,
        "is_thinking": vfe.is_analyzing,
        "frame_count": vfe.frame_count,
    }


@router.post("/ask")
@limiter.limit("10/minute")
async def ask_vlm(request: Request, body: QueryRequest, api_key: str = Depends(get_api_key)):
    if _is_prompt_injection(body.prompt):
        logger.warning(f"Prompt injection attempt blocked from request")
        return JSONResponse(
            content={"error": "Prompt contains disallowed patterns"}, status_code=400
        )

    vfe = get_engine()
    sm = get_stream_manager()
    first_cam = next(iter(Settings.SOURCES))
    success, frame = sm.get_frame(first_cam)
    if not success:
        return JSONResponse(
            content={"error": "Unable to capture frame from camera"}, status_code=500
        )
    vfe.process_frame(frame, user_query=body.prompt)
    return {"status": "Analysis started", "query": body.prompt}
