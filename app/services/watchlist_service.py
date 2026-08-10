import json

from app.database.database import SessionLocal
from app.database.models import User


def get_watchlist(telegram_id: str):

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.telegram_id == telegram_id)
            .first()
        )

        if not user or not user.watchlist:
            return []

        try:
            return json.loads(user.watchlist)
        except json.JSONDecodeError:
            return []

    finally:
        db.close()


def add_to_watchlist(
    telegram_id: str,
    symbol: str
):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.telegram_id == telegram_id)
            .first()
        )

        if not user:
            return False

        current_watchlist = []

        if user.watchlist:

            try:
                current_watchlist = json.loads(
                    user.watchlist
                )
            except json.JSONDecodeError:
                current_watchlist = []

        symbol = symbol.upper()

        if symbol not in current_watchlist:

            current_watchlist.append(symbol)

            user.watchlist = json.dumps(
                current_watchlist
            )

            db.commit()

        return True

    finally:
        db.close()


def remove_from_watchlist(
    telegram_id: str,
    symbol: str
):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.telegram_id == telegram_id)
            .first()
        )

        if not user:
            return False

        current_watchlist = []

        if user.watchlist:

            try:
                current_watchlist = json.loads(
                    user.watchlist
                )
            except json.JSONDecodeError:
                current_watchlist = []

        symbol = symbol.upper()

        if symbol in current_watchlist:

            current_watchlist.remove(symbol)

            user.watchlist = json.dumps(
                current_watchlist
            )

            db.commit()

        return True

    finally:
        db.close()