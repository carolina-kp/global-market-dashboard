import feedparser

def get_yahoo_news(ticker):
    """
    Fetch reliable Yahoo Finance RSS news for the given ticker.
    """
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}"
    feed = feedparser.parse(url)

    news_list = []
    for entry in feed.entries:
        news_list.append({
            "title": entry.get("title", "No title"),
            "published": entry.get("published", "No date"),
            "link": entry.get("link", "")
        })
    return news_list
