import os
from urllib.parse import unquote, urlparse

import pytest


TEST_DATABASE_NAME = "support_platform_test"


def database_name(database_url: str) -> str:
    return unquote(urlparse(database_url).path.lstrip("/"))


def validate_test_environment(app_env: str | None, database_url: str | None) -> None:
    if app_env != "test":
        raise pytest.UsageError(
            "Refusing to run tests: APP_ENV must be 'test'."
        )

    if not database_url:
        raise pytest.UsageError(
            "Refusing to run tests: DATABASE_URL is required."
        )

    if database_name(database_url) != TEST_DATABASE_NAME:
        raise pytest.UsageError(
            "Refusing to run tests: DATABASE_URL must use "
            f"the '{TEST_DATABASE_NAME}' database."
        )


def pytest_sessionstart(session: pytest.Session) -> None:
    validate_test_environment(
        app_env=os.environ.get("APP_ENV"),
        database_url=os.environ.get("DATABASE_URL"),
    )
