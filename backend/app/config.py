
import os
from pathlib import Path

from pydantic import BaseModel

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class Settings(BaseModel):
    shared_model_name: str = os.getenv("VERICLEAR_SHARED_MODEL", "gpt-4o-mini")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    use_real_intent_model: bool = os.getenv("USE_REAL_INTENT_MODEL", "true").lower() == "true"
    use_real_summarizer_model: bool = os.getenv("USE_REAL_SUMMARIZER_MODEL", "true").lower() == "true"
    auto_resolve_threshold: float = 0.85
    max_new_tokens: int = int(os.getenv("VERICLEAR_MAX_NEW_TOKENS", "256"))


settings = Settings()
