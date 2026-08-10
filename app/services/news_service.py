import requests

from app.config.settings import settings


def get_financial_news(query: str = "financial markets"):

    url = "https://newsapi.org/v2/everything"

    financial_query = (
        f'"{query}" AND '
        '(stock OR stocks OR earnings OR revenue OR '
        'market OR finance OR investment OR acquisition OR '
        'merger OR SEC OR investors)'
    )

    params = {
        "q": financial_query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": settings.NEWS_API_KEY,
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        articles = []

        for article in data.get("articles", []):

            title = article.get("title")
            description = article.get("description")
            source = article.get("source", {}).get("name")
            article_url = article.get("url")
            published_at = article.get("publishedAt")

            if not title:
                continue

            articles.append({
                "title": title,
                "description": description,
                "source": source,
                "url": article_url,
                "published_at": published_at,
            })

        return articles

    except Exception as e:

        print("News service error:", e)

        return []