from fastapi import APIRouter, Depends, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm.base import BaseLLMProvider
from app.services.llm.factory import get_llm_provider
from app.core.config import settings

# 1. This must be an APIRouter
router = APIRouter(prefix="/chat", tags=["AI Chat"])

# 2. This MUST be @router.post, NOT @app.post
@router.post("/ask", response_model=ChatResponse)
def ask_ai(
    payload: ChatRequest,
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