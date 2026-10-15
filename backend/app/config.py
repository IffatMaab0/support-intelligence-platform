import os


def get_database_url() -> str:
    database_url = os.environ["DATABASE_URL"]

    # Railway provides a standard PostgreSQL URL. SQLAlchemy needs the
    # installed psycopg v3 driver named explicitly.
    if database_url.startswith("postgresql://"):
        return database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    return database_url


DATABASE_URL = get_database_url()
