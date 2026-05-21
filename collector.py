import os
import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
SENTIMENT_URL = os.getenv("SENTIMENT_API_URL")
DATABASE_URL = os.getenv("DATABASE_URL")

TOPICS = ["technology", "science", "business", "health"]


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL UNIQUE,
            source TEXT,
            topic TEXT,
            sentiment TEXT,
            confidence REAL,
            fetched_at TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
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


def run():
    conn = init_db()
    cur = conn.cursor()
    now = datetime.utcnow()
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

            if not title:
                continue

            try:
                sentiment, confidence = analyze_sentiment(title)
            except Exception as e:
                print(f"  Sentiment error: {e}")
                continue

            try:
                cur.execute(
                    """INSERT INTO articles (title, source, topic, sentiment, confidence, fetched_at)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       ON CONFLICT (title) DO NOTHING""",
                    (title, source, topic, sentiment, confidence, now),
                )
                if cur.rowcount:
                    total += 1
            except Exception as e:
                print(f"  DB error: {e}")
                conn.rollback()

    conn.commit()
    cur.close()
    conn.close()
    print(f"Done — {total} new articles saved.")


if __name__ == "__main__":
    run()
