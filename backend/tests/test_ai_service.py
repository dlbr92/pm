import pytest

from app.services.ai_service import AIService, AIServiceError


class DummyChatCompletions:
    def __init__(self, content: str):
        self._content = content

    def create(self, **_kwargs):
        message = type("Message", (), {"content": self._content})()
        choice = type("Choice", (), {"message": message})()
        return type("Response", (), {"choices": [choice]})()


class DummyClient:
    def __init__(self, content: str):
        self.chat = type("Chat", (), {"completions": DummyChatCompletions(content)})()


def test_complete_text_uses_configured_model_and_returns_content() -> None:
    service = AIService(api_key="test-key", model="test-model", client=DummyClient("4"))
    response = service.complete_text("2+2")
    assert response == "4"


def test_complete_text_raises_for_empty_response() -> None:
    service = AIService(api_key="test-key", client=DummyClient(""))
    with pytest.raises(AIServiceError) as exc:
        service.complete_text("2+2")
    assert exc.value.status_code == 502


def test_service_requires_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(AIServiceError) as exc:
        AIService(api_key="")
    assert exc.value.status_code == 503
