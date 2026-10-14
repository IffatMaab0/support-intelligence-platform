from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db import engine
from app.main import app


client = TestClient(app)


def test_health_live() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_test_database_connection() -> None:
    with engine.connect() as connection:
        assert connection.execute(text("SELECT 1")).scalar_one() == 1
