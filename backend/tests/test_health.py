from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "backend"}


def test_root_serves_example_html() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Hello world from FastAPI static HTML." in response.text
