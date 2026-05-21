import os
import sqlite3
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
SENTIMENT_URL = os.getenv("SENTIMENT_API_URL")

TOPICS = ["technology", "science", "business", "health"]


def init_db():
    conn = sqlite3.connect("news.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            source TEXT,
            topic TEXT,
            sentiment TEXT,
            confidence REAL,
            fetched_at TEXT
        )
    """)
    conn.commit()
    return conn


def fetch_headlines(topic):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,
        "apiKey": NEWS_API_KEY,
    }
    res = requests.get(url, params=params, timeout=10)
    res.raise_for_status()
    return res.json().get("articles", [])


def analyze_sentiment(text):
    res = requests.post(SENTIMENT_URL, json={"text": text}, timeout=10)
    res.raise_for_status()
    data = res.json()
    return data.get("sentiment"), data.get("confidence")


def already_exists(conn, title):
    row = conn.execute("SELECT 1 FROM articles WHERE title = ?", (title,)).fetchone()
    return row is not None


def run():
    conn = init_db()
    now = datetime.utcnow().isoformat()
    total = 0

    for topic in TOPICS:
        print(f"Fetching: {topic}...")
        try:
            articles = fetch_headlines(topic)
        except Exception as e:
            print(f"  Error fetching {topic}: {e}")
            continue

        for article in articles:
            title = (article.get("title") or "").strip()
            source = (article.get("source") or {}).get("name", "Unknown")

            if not title or already_exists(conn, title):
                continue

            try:
                sentiment, confidence = analyze_sentiment(title)
            except Exception as e:
                print(f"  Sentiment error: {e}")
                continue

            conn.execute(
                "INSERT INTO articles (title, source, topic, sentiment, confidence, fetched_at) VALUES (?, ?, ?, ?, ?, ?)",
                (title, source, topic, sentiment, confidence, now),
            )
            total += 1

    conn.commit()
    conn.close()
    print(f"Done — {total} new articles saved.")


if __name__ == "__main__":
    run()
