from app.database.database import SessionLocal
from app.database.models import User


def get_or_create_user(telegram_id: str, name: str):

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.telegram_id == telegram_id)
            .first()
        )

        if user:
            return user

        user = User(
            telegram_id=telegram_id,
            name=name,
            briefing_time="09:00",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    finally:
        db.close()