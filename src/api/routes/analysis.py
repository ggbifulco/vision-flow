from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from src.api.deps import get_api_key, get_engine, get_stream_manager
from src.config.settings import Settings

router = APIRouter(tags=["Analysis"])


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
async def ask_vlm(request: QueryRequest, api_key: str = Depends(get_api_key)):
    vfe = get_engine()
    sm = get_stream_manager()
    first_cam = next(iter(Settings.SOURCES))
    success, frame = sm.get_frame(first_cam)
    if not success:
        return JSONResponse(
            content={"error": "Unable to capture frame from camera"}, status_code=500
        )
    vfe.process_frame(frame, user_query=request.prompt)
    return {"status": "Analysis started", "query": request.prompt}
