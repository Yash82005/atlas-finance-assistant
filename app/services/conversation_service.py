from app.database.database import SessionLocal
from app.database.models import ConversationMessage


def save_message(
    telegram_id: str,
    role: str,
    content: str
):
    db = SessionLocal()

    try:
        message = ConversationMessage(
            telegram_id=telegram_id,
            role=role,
            content=content
        )

        db.add(message)
        db.commit()

    finally:
        db.close()


def get_recent_messages(
    telegram_id: str,
    limit: int = 10
):
    db = SessionLocal()

    try:
        messages = (
            db.query(ConversationMessage)
            .filter(
                ConversationMessage.telegram_id == telegram_id
            )
            .order_by(
                ConversationMessage.created_at.desc()
            )
            .limit(limit)
            .all()
        )

        messages.reverse()

        return messages

    finally:
        db.close()