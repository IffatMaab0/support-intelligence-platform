from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_login_wrong_password():
    response = client.post(
        "/v1/auth/login",
        json={
            "email": "customer.a@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid email or password"
    }


def test_me_without_token():
    response = client.get("/v1/auth/me")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Not authenticated"
    }