import os

from openai import APIError, APITimeoutError, OpenAI

AI_MODEL = "gpt-4.1-mini"
AI_DIAGNOSTIC_PROMPT = "2+2"


class AIServiceError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AIService:
    def __init__(
        self,
        api_key: str | None = None,
        model: str = AI_MODEL,
        timeout_seconds: float = 20.0,
        client: OpenAI | None = None,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

        if not self.api_key:
            raise AIServiceError("OPENAI_API_KEY is not configured.", status_code=503)

        self.client = client or OpenAI(api_key=self.api_key, timeout=timeout_seconds)

    def complete_messages(self, messages: list[dict[str, str]]) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
        except APITimeoutError as exc:
            raise AIServiceError("AI request timed out.", status_code=504) from exc
        except APIError as exc:
            raise AIServiceError("AI request failed.", status_code=502) from exc
        except Exception as exc:
            raise AIServiceError("Unexpected AI request error.", status_code=500) from exc

        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise AIServiceError("AI returned an empty response.", status_code=502)

        return content.strip()

    def complete_text(self, prompt: str) -> str:
        return self.complete_messages([{"role": "user", "content": prompt}])

    def run_diagnostic(self) -> str:
        return self.complete_text(AI_DIAGNOSTIC_PROMPT)
