
from functools import lru_cache

from app.config import settings


@lru_cache(maxsize=2)
def load_chat_model():
    if not settings.openai_api_key:
        print("[ModelLoader] OPENAI_API_KEY missing; cannot create OpenAI client.")
        return None

    try:
        from openai import OpenAI
    except ImportError as exc:
        print(f"[ModelLoader] Failed to import OpenAI client: {exc}")
        return None

    try:
        client = OpenAI(api_key=settings.openai_api_key)
    except Exception as exc:
        print(f"[ModelLoader] Failed to initialize OpenAI client: {exc}")
        return None

    print("[ModelLoader] OpenAI client initialized successfully.")
    return client


def get_intent_model():
    if not settings.use_real_intent_model:
        return None
    return load_chat_model()


def get_summarizer_model():
    if not settings.use_real_summarizer_model:
        return None
    return load_chat_model()
