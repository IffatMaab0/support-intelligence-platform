import json
from getpass import getpass
from pathlib import Path

from sqlalchemy.orm import Session

from app.db import engine
from app.models import User, UserRole
from app.security import hash_password


USERS_FILE = Path("/data/demo/users.json")


def load_users() -> list[dict]:
    with USERS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def seed_users() -> None:
    users = load_users()

    with Session(engine) as session:
        for user_data in users:
            existing_user = session.query(User).filter(
                User.email == user_data["email"]
            ).first()

            if existing_user:
                print(f"Skipping existing user: {user_data['email']}")
                continue

            password = getpass(
                f"Enter password for {user_data['email']}: "
            )

            new_user = User(
                email=user_data["email"],
                display_name=user_data["display_name"],
                role=UserRole(user_data["role"]),
                password_hash=hash_password(password),
                is_active=True,
            )

            session.add(new_user)

        session.commit()

    print("User seeding complete.")


if __name__ == "__main__":
    seed_users()