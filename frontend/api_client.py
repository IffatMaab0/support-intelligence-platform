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


def create_ticket(
    token: str,
    subject: str,
    original_message: str,
) -> dict:
    response = requests.post(
        f"{API_URL}/v1/tickets",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "subject": subject,
            "original_message": original_message,
        },
    )

    response.raise_for_status()
    return response.json()


def list_tickets(
    token: str,
    search: str | None = None,
    skip: int = 0,
    limit: int = 10,
) -> dict:
    response = requests.get(
        f"{API_URL}/v1/tickets",
        headers={
            "Authorization": f"Bearer {token}",
        },
        params={
            "search": search,
            "skip": skip,
            "limit": limit,
        },
    )

    response.raise_for_status()
    return response.json()


def get_ticket(token: str, ticket_id: int) -> dict:
    response = requests.get(
        f"{API_URL}/v1/tickets/{ticket_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    response.raise_for_status()
    return response.json()


def list_agents(token: str) -> list:
    response = requests.get(
        f"{API_URL}/v1/meta/agents",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    response.raise_for_status()
    return response.json()


def assign_ticket(
    token: str,
    ticket_id: int,
    assigned_agent_id: str | None,
    expected_version: int,
) -> dict:
    response = requests.patch(
        f"{API_URL}/v1/tickets/{ticket_id}/assignment",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "assigned_agent_id": assigned_agent_id,
            "expected_version": expected_version,
        },
    )

    response.raise_for_status()
    return response.json()