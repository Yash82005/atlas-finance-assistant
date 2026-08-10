import json

from app.database.database import SessionLocal
from app.database.models import User


def update_user_profile(
    telegram_id: str,
    role: str | None = None,
    interests: list[str] | None = None,
    watchlist: list[str] | None = None,
):
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.telegram_id == telegram_id)
            .first()
        )

        if not user:
            return None

        if role:
            user.role = role

        if interests:
            user.interests = json.dumps(interests)

        if watchlist:
            user.watchlist = json.dumps(watchlist)

        db.commit()
        db.refresh(user)

        return user

    finally:
        db.close()