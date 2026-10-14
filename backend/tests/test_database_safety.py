import pytest

from conftest import TEST_DATABASE_NAME, validate_test_environment


def test_test_environment_accepts_the_dedicated_database() -> None:
    validate_test_environment(
        app_env="test",
        database_url=(
            "postgresql+psycopg://test_user:test_password@"
            f"test-db:5432/{TEST_DATABASE_NAME}"
        ),
    )


@pytest.mark.parametrize(
    ("app_env", "database_url"),
    [
        (
            "development",
            f"postgresql+psycopg://test-db:5432/{TEST_DATABASE_NAME}",
        ),
        (
            "test",
            "postgresql+psycopg://test-db:5432/support_platform",
        ),
    ],
)
def test_test_environment_rejects_unsafe_settings(
    app_env: str,
    database_url: str,
) -> None:
    with pytest.raises(pytest.UsageError):
        validate_test_environment(
            app_env=app_env,
            database_url=database_url,
        )
