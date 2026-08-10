import re


STOCK_SYMBOLS = {
    "nvidia": "NVDA",
    "apple": "AAPL",
    "microsoft": "MSFT",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "amazon": "AMZN",
    "tesla": "TSLA",
    "meta": "META",
    "amd": "AMD",
    "intel": "INTC",
    "netflix": "NFLX",
    "oracle": "ORCL",
    "palantir": "PLTR",
}


# Reverse mapping:
# NVDA -> NVDA
# AAPL -> AAPL
# etc.
VALID_TICKERS = set(STOCK_SYMBOLS.values())


def detect_financial_intent(message: str):

    text = message.lower().strip()

    # =================================================
    # Extract stock symbol/company
    # =================================================

    symbol = None

    # First check company names
    for company, ticker in STOCK_SYMBOLS.items():
        if re.search(rf"\b{re.escape(company)}\b", text):
            symbol = ticker
            break

    # If no company name was found, check ticker
    if symbol is None:
        ticker_match = re.search(
            r"\b[A-Z]{1,5}\b",
            message
        )

        if ticker_match:
            possible_symbol = ticker_match.group(0).upper()

            if possible_symbol in VALID_TICKERS:
                symbol = possible_symbol

    # =================================================
    # WATCHLIST
    # =================================================

    # Add to watchlist
    add_keywords = [
        "add",
        "put",
        "include",
        "save",
    ]

    if (
        "watchlist" in text
        and any(keyword in text for keyword in add_keywords)
    ):
        return {
            "intent": "add_watchlist",
            "symbol": symbol
        }

    # Remove from watchlist
    remove_keywords = [
        "remove",
        "delete",
        "drop",
    ]

    if (
        "watchlist" in text
        and any(keyword in text for keyword in remove_keywords)
    ):
        return {
            "intent": "remove_watchlist",
            "symbol": symbol
        }

    # Show watchlist
    show_keywords = [
        "show",
        "view",
        "list",
        "display",
        "see",
    ]

    if (
        "watchlist" in text
        and any(keyword in text for keyword in show_keywords)
    ):
        return {
            "intent": "show_watchlist",
            "symbol": None
        }

    # =================================================
    # STOCK PRICE
    # =================================================

    price_keywords = [
        "stock price",
        "share price",
        "trading at",
        "trading for",
        "price of",
        "how much is",
        "current price",
        "price",
    ]

    if any(keyword in text for keyword in price_keywords):

        if symbol:
            return {
                "intent": "stock_price",
                "symbol": symbol
            }

    # =================================================
    # FINANCIAL NEWS
    # =================================================

    news_keywords = [
        "news",
        "latest news",
        "financial news",
        "market news",
    ]

    if any(keyword in text for keyword in news_keywords):

        if symbol:
            company_name = next(
                (
                    company
                    for company, ticker in STOCK_SYMBOLS.items()
                    if ticker == symbol
                ),
                symbol
            )

            return {
                "intent": "company_news",
                "symbol": symbol,
                "query": company_name,
            }

        return {
            "intent": "financial_news",
            "symbol": None,
            "query": "financial markets",
        }

    # =================================================
    # COMPANY RESEARCH
    # =================================================

    research_keywords = [
        "tell me about",
        "company overview",
        "company profile",
        "business overview",
        "what does",
        "information about",
        "about",
    ]

    if any(keyword in text for keyword in research_keywords):

        if symbol:
            return {
                "intent": "company_research",
                "symbol": symbol
            }

    # =================================================
    # GENERAL FINANCE
    # =================================================

    finance_keywords = [
        "market",
        "earnings",
        "revenue",
        "profit",
        "valuation",
        "investment",
        "investing",
        "financial",
        "stocks",
    ]

    if any(keyword in text for keyword in finance_keywords):

        return {
            "intent": "general_finance",
            "symbol": symbol
        }

    # =================================================
    # GENERAL CHAT
    # =================================================

    return {
        "intent": "general_chat",
        "symbol": None
    }
