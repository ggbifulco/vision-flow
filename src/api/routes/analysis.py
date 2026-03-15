from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.api.deps import get_api_key, get_engine, get_stream_manager
from src.config.settings import Settings

router = APIRouter(tags=["Analysis"])

class QueryRequest(BaseModel):
    prompt: str

@router.get("/latest_analysis")
async def get_latest_analysis(api_key: str = Depends(get_api_key)):
    vfe = get_engine()
    return {
        "analysis": vfe.last_analysis,
        "is_thinking": vfe.is_analyzing,
        "frame_count": vfe.frame_count
    }

@router.post("/ask")
async def ask_vlm(request: QueryRequest, api_key: str = Depends(get_api_key)):
    vfe = get_engine()
    sm = get_stream_manager()
    # Usa la prima cam disponibile per il query snapshot
    success, frame = sm.get_frame(next(iter(Settings.SOURCES)))
    if not success:
        return JSONResponse(content={"error": "Cap error"}, status_code=500)
    vfe.process_frame(frame, user_query=request.prompt)
    return {"status": "Analysis started", "query": request.prompt}
