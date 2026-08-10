import yfinance as yf


def get_stock_price(symbol: str):

    ticker = yf.Ticker(symbol)

    history = ticker.history(period="2d")

    if history.empty:
        return None

    latest = history.iloc[-1]

    price = float(latest["Close"])

    previous_close = None

    if len(history) >= 2:
        previous_close = float(history.iloc[-2]["Close"])

    change = None
    change_percent = None

    if previous_close:
        change = price - previous_close
        change_percent = (change / previous_close) * 100

    return {
        "symbol": symbol.upper(),
        "price": round(price, 2),
        "previous_close": (
            round(previous_close, 2)
            if previous_close
            else None
        ),
        "change": (
            round(change, 2)
            if change is not None
            else None
        ),
        "change_percent": (
            round(change_percent, 2)
            if change_percent is not None
            else None
        ),
    }