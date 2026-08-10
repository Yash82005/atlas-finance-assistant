import json

from app.database.database import SessionLocal
from app.database.models import User
from app.services.finance_service import get_stock_price


def check_watchlist_alerts(
    telegram_id: str,
    threshold: float = 1.0
):
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.telegram_id == telegram_id)
            .first()
        )

        if not user:
            return []

        # -----------------------------
        # Get watchlist
        # -----------------------------

        try:
            watchlist = (
                json.loads(user.watchlist)
                if user.watchlist
                else []
            )
        except (json.JSONDecodeError, TypeError):
            watchlist = []

        alerts = []

        # -----------------------------
        # Check each stock
        # -----------------------------

        for symbol in watchlist[:5]:

            data = get_stock_price(symbol)

            if not data:
                continue

            change_percent = data.get("change_percent")

            if change_percent is None:
                continue

            # Only alert when movement reaches threshold
            if abs(change_percent) < threshold:
                continue

            direction = "UP" if change_percent > 0 else "DOWN"

            # Unique alert identifier
            alert_key = (
                f"{symbol.upper()}:{direction}:"
                f"{round(change_percent, 1)}"
            )

            # -----------------------------
            # Prevent duplicate alert
            # -----------------------------

            if user.last_alerts == alert_key:
                continue

            alerts.append(
                f"🚨 {symbol.upper()} 📈 {direction}\n"
                f"Price: ${data.get('price', 0):.2f}\n"
                f"Daily change: {change_percent:+.2f}%"
            )

            # Save latest alert
            user.last_alerts = alert_key

        db.commit()

        return alerts

    finally:
        db.close()