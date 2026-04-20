from fastapi.testclient import TestClient

from app.main import app
from app.routers.ai import get_ai_service
from app.services.ai_service import AIServiceError


class FakeAIService:
    model = "gpt-4.1-mini"

    def __init__(self, response: str | None = None, error: AIServiceError | None = None):
        self._response = response
        self._error = error

    def run_diagnostic(self) -> str:
        if self._error is not None:
            raise self._error
        return self._response or "4"


def test_ai_diagnostic_success_with_mocked_service() -> None:
    app.dependency_overrides[get_ai_service] = lambda: FakeAIService(response="4")
    try:
        with TestClient(app) as client:
            response = client.get("/api/ai/diagnostic")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["prompt"] == "2+2"
    assert payload["response"] == "4"
    assert payload["model"] == "gpt-4.1-mini"


def test_ai_diagnostic_maps_timeout_to_504() -> None:
    app.dependency_overrides[get_ai_service] = lambda: FakeAIService(
        error=AIServiceError("AI request timed out.", status_code=504)
    )
    try:
        with TestClient(app) as client:
            response = client.get("/api/ai/diagnostic")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 504
    assert response.json()["detail"] == "AI request timed out."


def test_ai_diagnostic_maps_upstream_failure_to_502() -> None:
    app.dependency_overrides[get_ai_service] = lambda: FakeAIService(
        error=AIServiceError("AI request failed.", status_code=502)
    )
    try:
        with TestClient(app) as client:
            response = client.get("/api/ai/diagnostic")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json()["detail"] == "AI request failed."
