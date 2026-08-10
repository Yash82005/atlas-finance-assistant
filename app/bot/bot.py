import json
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from app.config.settings import settings
from app.ai.gemini_client import client

from app.services.user_service import get_or_create_user

from app.services.conversation_service import (
    save_message,
    get_recent_messages,
)

from app.ai.intent_detector import detect_financial_intent

from app.services.finance_service import get_stock_price
from app.services.company_service import get_company_info
from app.services.news_service import get_financial_news

from app.services.watchlist_service import (
    get_watchlist,
    add_to_watchlist,
    remove_from_watchlist,
)

from app.services.onboarding_service import update_user_profile

from app.database.database import SessionLocal
from app.database.models import User

from app.services.briefing_service import generate_briefing
from telegram.request import HTTPXRequest


# =========================================================
# START COMMAND
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    telegram_user = update.effective_user
    telegram_id = str(telegram_user.id)

    user = get_or_create_user(
        telegram_id=telegram_id,
        name=telegram_user.first_name
    )

    # -----------------------------------------------------
    # Existing completed user
    # -----------------------------------------------------

    if user.onboarding_completed:

        await update.message.reply_text(
            f"👋 Welcome back, {user.name}!\n\n"
            "I'm Atlas AI, your personal financial assistant.\n\n"
            "You can ask me about:\n"
            "• Stock prices\n"
            "• Companies\n"
            "• Financial news\n"
            "• Your watchlist\n"
            "• Personalized briefings\n\n"
            "Use /briefing for your personalized financial briefing."
        )

        return

    # -----------------------------------------------------
    # Existing user with role but no interests
    # -----------------------------------------------------

    if user.role and not user.interests:

        context.user_data["onboarding_step"] = "interests"

        await update.message.reply_text(
            "Thanks! 👍\n\n"
            "What are your main financial interests?\n\n"
            "For example:\n"
            "• Investing\n"
            "• Saving\n"
            "• Stocks\n"
            "• Crypto\n"
            "• Learning finance\n\n"
            "You can list multiple interests."
        )

        return

    # -----------------------------------------------------
    # New user
    # -----------------------------------------------------

    context.user_data["onboarding_step"] = "role"

    await update.message.reply_text(
        f"👋 Hi {user.name}!\n\n"
        "I'm Atlas AI, your personal financial assistant.\n\n"
        "I'd like to understand how I can be most useful.\n\n"
        "What best describes your role?\n\n"
        "Examples:\n"
        "• Student\n"
        "• Investor\n"
        "• Trader\n"
        "• Financial professional\n"
        "• Beginner"
    )


# =========================================================
# MESSAGE HANDLER
# =========================================================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_message = update.message.text.strip()
    telegram_id = str(update.effective_user.id)

    try:

        # =================================================
        # 1. GET USER
        # =================================================

        user = get_or_create_user(
            telegram_id=telegram_id,
            name=update.effective_user.first_name
        )

        print("========== USER PROFILE ==========")
        print("Role:", user.role)

        try:
            interests = (
                json.loads(user.interests)
                if user.interests
                else []
            )
        except (json.JSONDecodeError, TypeError):
            interests = []

        print("Interests:", interests)
        print(
            "Onboarding completed:",
            user.onboarding_completed
        )
        print("==================================")

        # =================================================
        # 2. ONBOARDING
        # =================================================

        if not user.onboarding_completed:

            onboarding_step = context.user_data.get(
                "onboarding_step"
            )

            # Recover state after bot restart
            if not onboarding_step:

                if user.role and not user.interests:
                    onboarding_step = "interests"
                else:
                    onboarding_step = "role"

                context.user_data["onboarding_step"] = (
                    onboarding_step
                )

            # -------------------------------------------------
            # STEP 1: ROLE
            # -------------------------------------------------

            if onboarding_step == "role":

                role = user_message

                if not role:

                    await update.message.reply_text(
                        "Please tell me your role, for example "
                        "Student, Investor, Trader, or Beginner."
                    )

                    return

                update_user_profile(
                    telegram_id=telegram_id,
                    role=role
                )

                context.user_data["onboarding_step"] = (
                    "interests"
                )

                save_message(
                    telegram_id=telegram_id,
                    role="user",
                    content=user_message
                )

                assistant_message = (
                    "Thanks! 👍\n\n"
                    "What are your main financial interests?\n\n"
                    "For example:\n"
                    "• Investing\n"
                    "• Saving\n"
                    "• Stocks\n"
                    "• Crypto\n"
                    "• Learning finance\n\n"
                    "You can list multiple interests."
                )

                save_message(
                    telegram_id=telegram_id,
                    role="assistant",
                    content=assistant_message
                )

                await update.message.reply_text(
                    assistant_message
                )

                return

            # -------------------------------------------------
            # STEP 2: INTERESTS
            # -------------------------------------------------

            if onboarding_step == "interests":

                interests = [
                    item.strip()
                    for item in user_message.split(",")
                    if item.strip()
                ]

                if not interests:

                    await update.message.reply_text(
                        "Please provide at least one financial "
                        "interest, such as Investing, Stocks, "
                        "Saving, or Crypto."
                    )

                    return

                update_user_profile(
                    telegram_id=telegram_id,
                    interests=interests
                )

                # Mark onboarding complete
                db = SessionLocal()

                try:

                    db_user = (
                        db.query(User)
                        .filter(
                            User.telegram_id == telegram_id
                        )
                        .first()
                    )

                    if db_user:

                        db_user.onboarding_completed = 1
                        db.commit()

                        saved_role = db_user.role

                    else:

                        saved_role = user.role

                finally:

                    db.close()

                context.user_data["onboarding_step"] = (
                    "completed"
                )

                save_message(
                    telegram_id=telegram_id,
                    role="user",
                    content=user_message
                )

                assistant_message = (
                    "✅ Profile setup complete!\n\n"
                    f"Role: {saved_role}\n"
                    f"Interests: {', '.join(interests)}\n\n"
                    "You can now ask me about:\n"
                    "• Stock prices\n"
                    "• Companies\n"
                    "• Financial news\n"
                    "• Your watchlist\n"
                    "• Personalized briefings"
                )

                save_message(
                    telegram_id=telegram_id,
                    role="assistant",
                    content=assistant_message
                )

                await update.message.reply_text(
                    assistant_message
                )

                return

        # =================================================
        # 3. SAVE USER MESSAGE
        # =================================================

        save_message(
            telegram_id=telegram_id,
            role="user",
            content=user_message
        )

        # =================================================
        # 4. DETECT INTENT
        # =================================================

        intent_data = detect_financial_intent(
            user_message
        )

        print(
            "Detected intent:",
            intent_data
        )

        intent = intent_data.get("intent")

        # =================================================
        # 5. ADD TO WATCHLIST
        # =================================================

        if intent == "add_watchlist":

            symbol = intent_data.get("symbol")

            if not symbol:

                await update.message.reply_text(
                    "Please tell me which stock you want to add."
                )

                return

            success = add_to_watchlist(
                telegram_id=telegram_id,
                symbol=symbol
            )

            if success:

                assistant_message = (
                    f"✅ {symbol.upper()} has been added "
                    "to your watchlist."
                )

            else:

                assistant_message = (
                    "❌ I couldn't update your watchlist."
                )

            save_message(
                telegram_id=telegram_id,
                role="assistant",
                content=assistant_message
            )

            await update.message.reply_text(
                assistant_message
            )

            return

        # =================================================
        # 6. REMOVE FROM WATCHLIST
        # =================================================

        if intent == "remove_watchlist":

            symbol = intent_data.get("symbol")

            if not symbol:

                await update.message.reply_text(
                    "Please tell me which stock you want to remove."
                )

                return

            success = remove_from_watchlist(
                telegram_id=telegram_id,
                symbol=symbol
            )

            if success:

                assistant_message = (
                    f"✅ {symbol.upper()} has been removed "
                    "from your watchlist."
                )

            else:

                assistant_message = (
                    "❌ I couldn't update your watchlist."
                )

            save_message(
                telegram_id=telegram_id,
                role="assistant",
                content=assistant_message
            )

            await update.message.reply_text(
                assistant_message
            )

            return

        # =================================================
        # 7. SHOW WATCHLIST
        # =================================================

        if intent == "show_watchlist":

            watchlist = get_watchlist(
                telegram_id=telegram_id
            )

            if watchlist:

                assistant_message = (
                    "📋 Your Watchlist\n\n"
                    + "\n".join(
                        f"• {symbol}"
                        for symbol in watchlist
                    )
                )

            else:

                assistant_message = (
                    "📋 Your watchlist is empty."
                )

            save_message(
                telegram_id=telegram_id,
                role="assistant",
                content=assistant_message
            )

            await update.message.reply_text(
                assistant_message
            )

            return

        # =================================================
        # 8. STOCK PRICE
        # =================================================

        if intent == "stock_price":

            symbol = intent_data.get("symbol")

            if symbol:

                market_data = get_stock_price(symbol)

                if market_data:

                    change = market_data.get("change")
                    change_percent = market_data.get(
                        "change_percent"
                    )

                    if (
                        change is not None
                        and change_percent is not None
                    ):

                        direction = (
                            "📈"
                            if change >= 0
                            else "📉"
                        )

                        assistant_message = (
                            f"{direction} "
                            f"{market_data['symbol']}\n\n"
                            f"Current price: "
                            f"${market_data['price']:.2f}\n"
                            f"Daily change: "
                            f"{change:+.2f} "
                            f"({change_percent:+.2f}%)"
                        )

                    else:

                        assistant_message = (
                            f"📊 "
                            f"{market_data['symbol']}\n\n"
                            f"Current price: "
                            f"${market_data['price']:.2f}"
                        )

                    save_message(
                        telegram_id=telegram_id,
                        role="assistant",
                        content=assistant_message
                    )

                    await update.message.reply_text(
                        assistant_message
                    )

                    return

            assistant_message = (
                "I couldn't find stock price data "
                "for that symbol."
            )

            save_message(
                telegram_id=telegram_id,
                role="assistant",
                content=assistant_message
            )

            await update.message.reply_text(
                assistant_message
            )

            return

        # =================================================
        # 9. FINANCIAL NEWS
        # =================================================

        if intent in [
            "company_news",
            "financial_news"
        ]:

            query = intent_data.get(
                "query",
                "financial markets"
            )

            news = get_financial_news(query)

            if news:

                lines = [
                    f"📰 Latest News: {query.title()}"
                ]

                for index, article in enumerate(
                    news[:5],
                    start=1
                ):

                    title = article.get(
                        "title",
                        "Untitled"
                    )

                    source = article.get(
                        "source",
                        "Unknown source"
                    )

                    lines.append(
                        f"\n{index}. {title}\n"
                        f"Source: {source}"
                    )

                assistant_message = "\n".join(lines)

                save_message(
                    telegram_id=telegram_id,
                    role="assistant",
                    content=assistant_message
                )

                await update.message.reply_text(
                    assistant_message
                )

                return

            assistant_message = (
                f"I couldn't find recent financial "
                f"news for {query}."
            )

            save_message(
                telegram_id=telegram_id,
                role="assistant",
                content=assistant_message
            )

            await update.message.reply_text(
                assistant_message
            )

            return

        # =================================================
        # 10. COMPANY RESEARCH
        # =================================================

        if intent == "company_research":

            symbol = intent_data.get("symbol")

            if symbol:

                company_data = get_company_info(symbol)

                if company_data:

                    market_cap = company_data.get(
                        "market_cap"
                    )

                    revenue = company_data.get(
                        "revenue"
                    )

                    profit = company_data.get(
                        "profit"
                    )

                    pe_ratio = company_data.get(
                        "pe_ratio"
                    )

                    market_cap_text = (
                        f"{market_cap:,}"
                        if isinstance(
                            market_cap,
                            (int, float)
                        )
                        else "N/A"
                    )

                    revenue_text = (
                        f"{revenue:,}"
                        if isinstance(
                            revenue,
                            (int, float)
                        )
                        else "N/A"
                    )

                    profit_text = (
                        f"{profit:,}"
                        if isinstance(
                            profit,
                            (int, float)
                        )
                        else "N/A"
                    )

                    assistant_message = (
                        f"🏢 "
                        f"{company_data.get('name', symbol)}\n\n"
                        f"📌 Sector: "
                        f"{company_data.get('sector', 'N/A')}\n"
                        f"📌 Industry: "
                        f"{company_data.get('industry', 'N/A')}\n\n"
                        f"💰 Market Cap: "
                        f"{market_cap_text}\n"
                        f"💵 Revenue: "
                        f"{revenue_text}\n"
                        f"📈 Profit: "
                        f"{profit_text}\n"
                        f"📊 P/E Ratio: "
                        f"{pe_ratio if pe_ratio is not None else 'N/A'}\n\n"
                        f"About:\n"
                        f"{company_data.get('description', 'No description available.')}"
                    )

                    save_message(
                        telegram_id=telegram_id,
                        role="assistant",
                        content=assistant_message
                    )

                    await update.message.reply_text(
                        assistant_message
                    )

                    return

            assistant_message = (
                "I couldn't find company information "
                "for that symbol."
            )

            save_message(
                telegram_id=telegram_id,
                role="assistant",
                content=assistant_message
            )

            await update.message.reply_text(
                assistant_message
            )

            return

        # =================================================
        # 11. NORMAL AI CHAT
        # =================================================

        history = get_recent_messages(
            telegram_id=telegram_id,
            limit=10
        )

        conversation = []

        for message in history:

            conversation.append({
                "role": message.role,
                "content": message.content
            })

        # Refresh user
        user = get_or_create_user(
            telegram_id=telegram_id,
            name=update.effective_user.first_name
        )

        try:

            interests = (
                json.loads(user.interests)
                if user.interests
                else []
            )

        except (json.JSONDecodeError, TypeError):

            interests = []

        print("========== USER PROFILE ==========")
        print("Role:", user.role)
        print("Interests:", interests)
        print("==================================")

        interests_text = (
            ", ".join(interests)
            if interests
            else "Not specified"
        )

        prompt = f"""
You are Atlas AI, a personal financial assistant.

Your job is to help users understand financial topics
clearly, responsibly, and practically.

## USER PROFILE

Role: {user.role or "Not specified"}
Financial interests: {interests_text}

## PERSONALIZATION RULES

1. Use the user's role and financial interests when
   relevant to the question.

2. Adjust explanations to the user's experience level.

3. Avoid unnecessarily advanced terminology.

4. Focus on the user's financial interests when
   relevant.

5. Do not unnecessarily repeat the user's profile.

6. Do not assume the user wants to buy or sell
   a specific investment.

7. Provide educational and balanced financial
   information.

8. Do not guarantee profits or future returns.

## CONVERSATION HISTORY

{conversation}

## CURRENT USER MESSAGE

{user_message}

Answer naturally and concisely.
"""

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        assistant_message = response.text

        save_message(
            telegram_id=telegram_id,
            role="assistant",
            content=assistant_message
        )

        await update.message.reply_text(
            assistant_message
        )

    except Exception as e:

        print("========== ERROR ==========")
        print(type(e).__name__)
        print(str(e))
        print("===========================")

        await update.message.reply_text(
            "I couldn't process that right now. "
            "Please try again."
        )


# =========================================================
# PERSONALIZED BRIEFING
# =========================================================

async def briefing(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    telegram_id = str(update.effective_user.id)

    try:
        user = get_or_create_user(
            telegram_id=telegram_id,
            name=update.effective_user.first_name
        )

        if not user.onboarding_completed:
            await update.message.reply_text(
                "Please complete your profile setup first."
            )
            return

        await update.message.reply_text(
            "📊 Preparing your personalized briefing..."
        )

        assistant_message = generate_briefing(
            telegram_id
        )

        save_message(
            telegram_id=telegram_id,
            role="assistant",
            content=assistant_message
        )

        await update.message.reply_text(
            assistant_message
        )

    except Exception as e:
        print("========== BRIEFING ERROR ==========")
        print(type(e).__name__)
        print(str(e))
        print("====================================")

        await update.message.reply_text(
            "⚠️ Your profile and watchlist are working, "
            "but I couldn't generate the briefing right now. "
            "Please try again."
        )

async def set_briefing(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    telegram_id = str(update.effective_user.id)

    # Check that a time was provided
    if not context.args:
        await update.message.reply_text(
            "⏰ Please provide a time.\n\n"
            "Example:\n"
            "/setbriefing 09:00"
        )
        return

    briefing_time = context.args[0]

    # Validate HH:MM format
    import re

    if not re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", briefing_time):
        await update.message.reply_text(
            "❌ Invalid time format.\n\n"
            "Please use HH:MM format.\n"
            "Example: /setbriefing 09:00"
        )
        return

    # Update database
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.telegram_id == telegram_id)
            .first()
        )

        if not user:
            await update.message.reply_text(
                "❌ User profile not found."
            )
            return

        user.briefing_time = briefing_time
        db.commit()

    finally:
        db.close()

    await update.message.reply_text(
        f"✅ Your daily briefing time has been set to "
        f"{briefing_time}."
    )

async def scheduled_briefing(
    context: ContextTypes.DEFAULT_TYPE
):
    db = SessionLocal()

    try:
        users = (
            db.query(User)
            .filter(
                User.onboarding_completed == 1,
                User.briefing_time.isnot(None)
            )
            .all()
        )

        current_time = datetime.now().strftime("%H:%M")

        for user in users:

            if user.briefing_time != current_time:
                continue

            try:
                # Generate personalized briefing
                from app.services.briefing_service import generate_briefing

                assistant_message = generate_briefing(
                    user.telegram_id
                )

                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text=assistant_message
                )

                save_message(
                    telegram_id=user.telegram_id,
                    role="assistant",
                    content=assistant_message
                )

                print(
                    f"✅ Scheduled briefing sent to "
                    f"{user.telegram_id}"
                )

            except Exception as e:
                print(
                    f"❌ Briefing failed for "
                    f"{user.telegram_id}: {e}"
                )

    finally:
        db.close()
async def set_briefing(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    telegram_id = str(update.effective_user.id)

    if not context.args:
        await update.message.reply_text(
            "Usage:\n"
            "/setbriefing 09:00\n\n"
            "Example:\n"
            "/setbriefing 18:30"
        )
        return

    briefing_time = context.args[0]

    # Validate HH:MM format
    import re

    if not re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", briefing_time):
        await update.message.reply_text(
            "❌ Invalid time format.\n\n"
            "Please use HH:MM, for example:\n"
            "/setbriefing 09:00"
        )
        return

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.telegram_id == telegram_id)
            .first()
        )

        if not user:
            await update.message.reply_text(
                "❌ User profile not found. Please use /start first."
            )
            return

        user.briefing_time = briefing_time
        db.commit()

        await update.message.reply_text(
            f"✅ Your daily briefing time has been set to "
            f"{briefing_time}."
        )

    except Exception as e:
        db.rollback()

        print("Set briefing error:", type(e).__name__, str(e))

        await update.message.reply_text(
            "❌ I couldn't update your briefing time."
        )

    finally:
        db.close()

async def myprofile(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    telegram_id = str(update.effective_user.id)

    user = get_or_create_user(
        telegram_id=telegram_id,
        name=update.effective_user.first_name
    )

    try:
        interests = (
            json.loads(user.interests)
            if user.interests
            else []
        )
    except (json.JSONDecodeError, TypeError):
        interests = []

    watchlist = get_watchlist(
        telegram_id=telegram_id
    )

    message = (
        "👤 Your Atlas AI Profile\n\n"
        f"Name: {user.name or 'Not set'}\n"
        f"Role: {user.role or 'Not set'}\n"
        f"Interests: {', '.join(interests) if interests else 'Not set'}\n"
        f"Watchlist: {', '.join(watchlist) if watchlist else 'Empty'}\n"
        f"Briefing time: {user.briefing_time or '09:00'}"
    )

    await update.message.reply_text(message)


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = (
        "🤖 Atlas AI Help\n\n"
        "📈 Stocks\n"
        "• What is the price of NVDA?\n"
        "• Tell me about Apple\n"
        "• Show me financial news\n\n"
        
        "📋 Watchlist\n"
        "• Add NVDA to my watchlist\n"
        "• Remove NVDA from my watchlist\n"
        "• Show my watchlist\n\n"
        
        "📊 Personalized Briefing\n"
        "• /briefing — Get your personalized financial briefing\n\n"
        
        "👤 Profile\n"
        "• /myprofile — View your profile\n\n"
        
        "❓ Help\n"
        "• /help — Show this help message\n\n"
        
        "💡 Atlas AI provides educational financial information "
        "and does not provide guaranteed investment returns."
    )

    await update.message.reply_text(message)


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):
    print("========== TELEGRAM ERROR ==========")
    print(type(context.error).__name__)
    print(str(context.error))
    print("====================================")

async def watchlist_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    telegram_id = str(update.effective_user.id)

    try:
        watchlist = get_watchlist(
            telegram_id=telegram_id
        )

        if watchlist:
            message = (
                "📋 Your Watchlist\n\n"
                + "\n".join(
                    f"• {symbol}"
                    for symbol in watchlist
                )
            )
        else:
            message = (
                "📋 Your Watchlist is empty.\n\n"
                "Add a stock by saying:\n"
                "\"add NVDA to my watchlist\""
            )

        await update.message.reply_text(message)

    except Exception as e:
        print("Watchlist command error:", type(e).__name__, str(e))

        await update.message.reply_text(
            "❌ I couldn't retrieve your watchlist right now."
        )

async def scheduled_alerts(context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()

    try:
        users = (
            db.query(User)
            .filter(
                User.onboarding_completed == 1,
                User.watchlist.isnot(None)
            )
            .all()
        )

        for user in users:
            try:
                from app.services.alert_service import check_watchlist_alerts

                alerts = check_watchlist_alerts(
                    telegram_id=user.telegram_id,
                    threshold=1.0
                )

                for alert in alerts:

                    message = (
                        f"🚨 Atlas Alert\n\n"
                        f"{alert}"
                    )

                    await context.bot.send_message(
                        chat_id=user.telegram_id,
                        text=message
                    )

                    print(
                        f"🚨 Alert sent to "
                        f"{user.telegram_id}"
                    )

            except Exception as e:
                print(
                    f"❌ Alert failed for "
                    f"{user.telegram_id}: "
                    f"{type(e).__name__}: {e}"
                )

    finally:
        db.close()
# =========================================================
# CREATE BOT
# =========================================================

def create_bot():

    request = HTTPXRequest(
    connect_timeout=30.0,
    read_timeout=30.0,
    write_timeout=30.0,
    pool_timeout=30.0,
)

    application = (
    Application.builder()
    .token(settings.TELEGRAM_BOT_TOKEN)
    .request(request)
    .build()
)

    # /start
    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # /briefing
    application.add_handler(
        CommandHandler(
            "briefing",
            briefing
        )
    )
    application.add_handler(
    CommandHandler(
        "watchlist",
        watchlist_command
    )
    )
    application.add_handler(
    CommandHandler(
        "myprofile",
        myprofile
    )
)

    application.add_handler(
    CommandHandler(
        "help",
        help_command
    )
)
    application.add_handler(
    CommandHandler(
        "setbriefing",
        set_briefing
    )
)

    # Normal messages
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )
    application.job_queue.run_repeating(
    scheduled_briefing,
    interval=60,
    first=10
)
    application.job_queue.run_repeating(
    scheduled_alerts,
    interval=300,
    first=20
)
    application.add_error_handler(error_handler)

    return application