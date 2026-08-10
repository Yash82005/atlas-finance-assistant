import json

from app.ai.gemini_client import client
from app.services.user_service import get_or_create_user
from app.services.watchlist_service import get_watchlist
from app.services.finance_service import get_stock_price
from app.services.news_service import get_financial_news


def generate_briefing(telegram_id: str):

    # -----------------------------
    # Get user
    # -----------------------------

    user = get_or_create_user(
        telegram_id=telegram_id,
        name=""
    )

    # -----------------------------
    # User interests
    # -----------------------------

    try:
        interests = (
            json.loads(user.interests)
            if user.interests
            else []
        )
    except (json.JSONDecodeError, TypeError):
        interests = []

    # -----------------------------
    # Watchlist
    # -----------------------------

    watchlist = get_watchlist(
        telegram_id=telegram_id
    )

    market_data = []

    for symbol in watchlist[:5]:

        data = get_stock_price(symbol)

        if data:

            price = data.get("price")
            change = data.get("change")
            change_percent = data.get("change_percent")

            if price is not None:

                if (
                    change is not None
                    and change_percent is not None
                ):

                    direction = (
                        "📈"
                        if change >= 0
                        else "📉"
                    )

                    market_data.append(
                        f"{direction} {symbol}: "
                        f"${price:.2f} "
                        f"({change:+.2f}, "
                        f"{change_percent:+.2f}%)"
                    )

                else:

                    market_data.append(
                        f"📊 {symbol}: ${price:.2f}"
                    )

    market_text = (
        "\n".join(market_data)
        if market_data
        else "No watchlist stocks."
    )

    # -----------------------------
    # Financial news
    # -----------------------------

    news = get_financial_news(
        "financial markets"
    )

    news_data = []

    for article in news[:5]:

        title = article.get(
            "title",
            "Untitled"
        )

        source = article.get(
            "source",
            "Unknown"
        )

        news_data.append(
            f"- {title} ({source})"
        )

    news_text = (
        "\n".join(news_data)
        if news_data
        else "No recent news available."
    )

    # -----------------------------
    # User profile text
    # -----------------------------

    interests_text = (
        ", ".join(interests)
        if interests
        else "Not specified"
    )

    watchlist_text = (
        ", ".join(watchlist)
        if watchlist
        else "Empty"
    )

    # -----------------------------
    # Gemini prompt
    # -----------------------------

    prompt = f"""
You are Atlas AI, a personal financial assistant.

Create a concise personalized financial briefing
for the user.

USER PROFILE

Name: {user.name or "User"}
Role: {user.role or "Not specified"}
Financial interests: {interests_text}

WATCHLIST

Stocks:
{watchlist_text}

Live market data:
{market_text}

RECENT FINANCIAL NEWS

{news_text}

REQUIREMENTS

1. Start with a short personalized greeting.
2. Summarize the user's watchlist using the provided
   market data.
3. Mention important financial news briefly.
4. Personalize the briefing around the user's
   financial interests.
5. Include one useful financial learning insight.
6. Only use market information provided above.
7. Do not invent financial data.
8. Do not guarantee returns.
9. Do not tell the user to buy or sell.
10. Keep the response concise and easy to read on Telegram.
11. Clearly state that the information is educational
    and not financial advice.

Return only the final Telegram briefing.
"""

    # -----------------------------
    # Generate briefing
    # -----------------------------

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text

