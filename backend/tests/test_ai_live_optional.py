import os

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set; skipping optional live AI connectivity test.",
)
def test_ai_diagnostic_live_returns_expected_math_signal() -> None:
    with TestClient(app) as client:
        response = client.get("/api/ai/diagnostic")

    assert response.status_code == 200
    payload = response.json()
    assert payload["prompt"] == "2+2"
    assert "4" in payload["response"]
