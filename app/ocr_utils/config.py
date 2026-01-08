import os
from mistralai import Mistral
from typing import Optional


class MistralClient:
    _client: Optional[Mistral] = None

    @classmethod
    def get_client(cls) -> Mistral:
        """
        Returns a singleton instance of Mistral client
        """
        if cls._client is None:
            api_key = os.getenv("MISTRAL_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "MISTRAL_API_KEY environment variable is not set"
                )

            cls._client = Mistral(api_key=api_key)

        return cls._client
