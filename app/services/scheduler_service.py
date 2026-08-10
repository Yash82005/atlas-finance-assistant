from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database.database import SessionLocal
from app.database.models import User
from app.services.briefing_service import generate_briefing


scheduler = AsyncIOScheduler()


async def send_daily_briefings(application):

    db = SessionLocal()

    try:

        users = (
            db.query(User)
            .filter(
                User.onboarding_completed == 1
            )
            .all()
        )

        for user in users:

            try:

                message = generate_briefing(
                    user.telegram_id
                )

                await application.bot.send_message(
                    chat_id=user.telegram_id,
                    text=message
                )

            except Exception as e:

                print(
                    f"Briefing failed for "
                    f"{user.telegram_id}: {e}"
                )

    finally:
        db.close()