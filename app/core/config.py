from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI AI Agent"
    
    # Provider selection: "ollama" or "openai"
    LLM_PROVIDER: str = "groq"
    
    # Ollama settings
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:1b"

    # Future providers (e.g. OpenAI)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Database Configuration
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_backend_db"

    # Security / Auth
    # In production, generate with: openssl rand -hex 32
    SECRET_KEY: str = "super-secret-development-key-change-in-production-12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15       # Short-lived (15 minutes)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7          # Long-lived (7 days)

    REDIS_URL: str = "redis://@localhost:6379/0"

    GROQ_API_KEY: str| None = Field(default=None)
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()