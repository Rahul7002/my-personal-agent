from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="User prompt or question")
    system_prompt: str | None = Field(
        default="You are an expert backend engineer. Be concise and precise.",
        description="Optional system persona instructions"
    )

class ChatResponse(BaseModel):
    response: str
    provider: str
    model: str