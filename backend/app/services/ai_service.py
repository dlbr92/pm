import os

from openai import APIError, APITimeoutError, OpenAI

AI_MODEL = "openai/gpt-oss-120b"
AI_FALLBACK_MODEL = "gpt-4.1-mini"
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
        model: str | None = None,
        fallback_model: str | None = None,
        base_url: str | None = None,
        timeout_seconds: float = 20.0,
        client: OpenAI | None = None,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", AI_MODEL)
        self.fallback_model = fallback_model or os.getenv(
            "OPENAI_FALLBACK_MODEL", AI_FALLBACK_MODEL
        )
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.last_used_model = self.model

        if not self.api_key:
            raise AIServiceError("OPENAI_API_KEY is not configured.", status_code=503)

        self.client = client or OpenAI(
            api_key=self.api_key,
            timeout=timeout_seconds,
            base_url=self.base_url,
        )

    def complete_messages(self, messages: list[dict[str, str]]) -> str:
        response = None
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            self.last_used_model = self.model
        except APITimeoutError as exc:
            raise AIServiceError("AI request timed out.", status_code=504) from exc
        except APIError as exc:
            exc_message = str(exc)
            invalid_model = "invalid model id" in exc_message.lower()
            if (
                invalid_model
                and self.fallback_model
                and self.fallback_model != self.model
            ):
                try:
                    response = self.client.chat.completions.create(
                        model=self.fallback_model,
                        messages=messages,
                    )
                    self.last_used_model = self.fallback_model
                except APITimeoutError as fallback_exc:
                    raise AIServiceError(
                        "AI request timed out.",
                        status_code=504,
                    ) from fallback_exc
                except APIError as fallback_exc:
                    raise AIServiceError(
                        f"AI request failed: {fallback_exc}",
                        status_code=502,
                    ) from fallback_exc
            else:
                raise AIServiceError(
                    f"AI request failed: {exc_message}",
                    status_code=502,
                ) from exc
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
