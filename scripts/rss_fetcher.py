"""RSS 피드에서 헤드라인 수집"""
import feedparser
from datetime import datetime, timedelta, timezone
import time


FEEDS = {
    "NYT-Business": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
    "NYT-World": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "NYT-Economy": "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml",
    "Reuters-Best": "https://reutersbest.com/feed/",
    "Reuters-Americas": "https://reutersbest.com/region/americas/feed/",
    "Reuters-Asia": "https://reutersbest.com/region/asia/feed/",
    "Yonhap-National": "https://en.yna.co.kr/RSS/news.xml",
    "Yonhap-Business": "https://en.yna.co.kr/RSS/economy.xml",
    "ElFinanciero": "https://www.elfinanciero.com.mx/arc/outboundfeeds/rss/?outputType=xml",
    "Banxico-Comunicados": "https://www.banxico.org.mx/RSS/RSS_PRIN.xml",
}


def fetch_all_feeds(hours_back=24):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    out = {}
    for name, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            items = []
            for entry in feed.entries[:25]:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published = datetime.fromtimestamp(time.mktime(entry.updated_parsed), tz=timezone.utc)

                if published and published < cutoff:
                    continue

                items.append({
                    "title": getattr(entry, "title", ""),
                    "summary": getattr(entry, "summary", "")[:500],
                    "link": getattr(entry, "link", ""),
                    "published": published.isoformat() if published else "",
                })
            if items:
                out[name] = items
        except Exception as e:
            print(f"[WARN] {name} fetch failed: {e}")
    return out


if __name__ == "__main__":
    res = fetch_all_feeds()
    for name, items in res.items():
        print(f"\n=== {name} ({len(items)} items) ===")
        for it in items[:3]:
            print(f"  - {it['title']}")
