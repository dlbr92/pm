import pytest
from openai import APIError

from app.services.ai_service import AIService, AIServiceError


class DummyChatCompletions:
    def __init__(self, responses: dict[str, str] | None = None, fail_models: set[str] | None = None):
        self._responses = responses or {}
        self._fail_models = fail_models or set()
        self.calls: list[str] = []

    def create(self, **kwargs):
        model = kwargs.get("model", "")
        self.calls.append(model)
        if model in self._fail_models:
            # Use APIError with a request object omitted to keep test simple.
            raise APIError(message="invalid model ID", request=None, body=None)
        content = self._responses.get(model, "4")
        message = type("Message", (), {"content": content})()
        choice = type("Choice", (), {"message": message})()
        return type("Response", (), {"choices": [choice]})()


class DummyClient:
    def __init__(self, completions: DummyChatCompletions):
        self.chat = type("Chat", (), {"completions": completions})()


def test_complete_text_uses_configured_model_and_returns_content() -> None:
    completions = DummyChatCompletions(responses={"test-model": "4"})
    service = AIService(
        api_key="test-key",
        model="test-model",
        client=DummyClient(completions),
    )
    response = service.complete_text("2+2")
    assert response == "4"


def test_complete_text_raises_for_empty_response() -> None:
    completions = DummyChatCompletions(responses={"openai/gpt-oss-120b": ""})
    service = AIService(api_key="test-key", client=DummyClient(completions))
    with pytest.raises(AIServiceError) as exc:
        service.complete_text("2+2")
    assert exc.value.status_code == 502


def test_complete_text_falls_back_when_primary_model_is_invalid() -> None:
    completions = DummyChatCompletions(
        responses={"gpt-4.1-mini": "4"},
        fail_models={"openai/gpt-oss-120b"},
    )
    service = AIService(api_key="test-key", client=DummyClient(completions))
    response = service.complete_text("2+2")

    assert response == "4"
    assert completions.calls == ["openai/gpt-oss-120b", "gpt-4.1-mini"]
    assert service.last_used_model == "gpt-4.1-mini"


def test_service_requires_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(AIServiceError) as exc:
        AIService(api_key="")
    assert exc.value.status_code == 503
