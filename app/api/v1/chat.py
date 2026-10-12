from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm.base import BaseLLMProvider
from app.services.llm.factory import get_llm_provider
from app.core.config import settings
from app.api.deps import get_current_user
from app.models.user import User
from app.core.limiter import limiter


# 1. This must be an APIRouter
router = APIRouter(prefix="/chat", tags=["AI Chat"])

# 2. This MUST be @router.post, NOT @app.post
@router.post("/ask", response_model=ChatResponse)
@limiter.limit("2/minute")
def ask_ai(
    request: Request,
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    llm: BaseLLMProvider = Depends(get_llm_provider),
):
    try:
        reply = llm.generate(
            prompt=payload.prompt,
            system_prompt=payload.system_prompt
        )
        return ChatResponse(
            response=reply,
            provider=settings.LLM_PROVIDER,
            model=settings.OLLAMA_MODEL if settings.LLM_PROVIDER == "ollama" else settings.OPENAI_MODEL
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream_chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    llm: BaseLLMProvider = Depends(get_llm_provider),
):
    token_stream = llm.generate_stream(
        prompt=payload.prompt,
        system_prompt=payload.system_prompt,
        model=settings.OLLAMA_MODEL,
    )

    return StreamingResponse(
        token_stream,
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Prevents Nginx/proxies from buffering chunks
        },
    )