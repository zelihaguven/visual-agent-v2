from fastapi.testclient import TestClient

from apps.api.main import create_app
from visual_agent.settings import Settings


def test_health_reports_service_is_up_and_login_is_off() -> None:
    client = TestClient(create_app(Settings(_env_file=None)))

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "auth_enabled": False}
