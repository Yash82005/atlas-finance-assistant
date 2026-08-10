import yfinance as yf


def get_company_info(symbol: str):

    ticker = yf.Ticker(symbol)

    info = ticker.info

    if not info:
        return None

    return {
        "symbol": symbol.upper(),
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "description": info.get("longBusinessSummary"),
        "market_cap": info.get("marketCap"),
        "revenue": info.get("totalRevenue"),
        "profit": info.get("netIncomeToCommon"),
        "pe_ratio": info.get("trailingPE"),
        "52_week_high": info.get("fiftyTwoWeekHigh"),
        "52_week_low": info.get("fiftyTwoWeekLow"),
    }