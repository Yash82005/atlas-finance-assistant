from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
)

from app.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    telegram_id = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    name = Column(String, nullable=True)
    role = Column(String, nullable=True)
    interests = Column(Text, nullable=True)
    watchlist = Column(Text, nullable=True)
    briefing_time = Column(String, nullable=True)

    last_briefing_date = Column(
    String,
    nullable=True
    )
    last_alerts = Column(
    String,
    nullable=True
    )

    onboarding_completed = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)

    telegram_id = Column(
        String,
        index=True,
        nullable=False
    )

    role = Column(
        String,
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )