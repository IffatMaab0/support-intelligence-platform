import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")


def login(email: str, password: str) -> dict:
    response = requests.post(
        f"{API_URL}/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    response.raise_for_status()
    return response.json()


def get_current_user(token: str) -> dict:
    response = requests.get(
        f"{API_URL}/v1/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    response.raise_for_status()
    return response.json()


def logout(token: str) -> None:
    requests.post(
        f"{API_URL}/v1/auth/logout",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )