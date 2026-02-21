from typing import Optional
from mistralai import Mistral
from google import genai
from app.core.config import settings


class MistralClient:
    _client: Optional[Mistral] = None

    @classmethod
    def get_client(cls) -> Mistral:
        if cls._client is None:
            if not settings.MISTRAL_API_KEY:
                raise RuntimeError("MISTRAL_API_KEY is not set")

            cls._client = Mistral(api_key=settings.MISTRAL_API_KEY)

        return cls._client

class GeminiClient:
    _client: Optional[genai.Client] = None

    @classmethod
    def get_client(cls) -> genai.Client:
        if cls._client is None:
            if not settings.GEMINI_API_KEY:
                raise RuntimeError("GEMINI_API_KEY is not set")

            cls._client = genai.Client(
                api_key=settings.GEMINI_API_KEY
            )

        return cls._client
