# News Sentiment Dashboard

A real-time dashboard that fetches news headlines, analyzes their sentiment using a custom-built RoBERTa API, and visualizes trends across topics.

## Demo

> Live demo: _coming soon_

## Features

- Fetches headlines from 100+ news sources via NewsAPI (technology, science, business, health)
- Analyzes sentiment of each headline using a [custom Sentiment Analysis API](https://github.com/vnetsiou/sentiment-api)
- Stores results in PostgreSQL with deduplication
- Auto-refreshes every 6 hours via a scheduled collector
- Interactive filters by topic and sentiment
- Pie chart, bar chart, and headline feed with confidence scores

## Tech Stack

| Layer | Technology |
|---|---|
| Data Source | [NewsAPI](https://newsapi.org/) |
| Sentiment Analysis | [Custom FastAPI + RoBERTa API](https://github.com/vnetsiou/sentiment-api) |
| Storage | PostgreSQL |
| Dashboard | [Streamlit](https://streamlit.io/) |
| Scheduler | APScheduler |
| Deployment | Railway |

## Architecture

```
NewsAPI → collector.py → Sentiment API → PostgreSQL → Streamlit Dashboard
```

The collector runs every 6 hours, fetches the latest headlines, sends each title to the Sentiment API, and stores the result. The dashboard reads from PostgreSQL and renders live charts.

## Run Locally

**Requirements:** Python 3.10+, PostgreSQL or SQLite for local dev

```bash
git clone https://github.com/vnetsiou/news-dashboard.git
cd news-dashboard

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Fill in your NEWS_API_KEY and DATABASE_URL

# Collect data
python collector.py

# Run dashboard
streamlit run dashboard.py
```

## Environment Variables

| Variable | Description |
|---|---|
| `NEWS_API_KEY` | Your NewsAPI key from newsapi.org |
| `SENTIMENT_API_URL` | URL of the Sentiment Analysis API |
| `DATABASE_URL` | PostgreSQL connection string |

## Related Projects

- [Sentiment Analysis API](https://github.com/vnetsiou/sentiment-api) — the ML API powering this dashboard

## Author

**Vasiliki Netsiou** — Full Stack Developer  
[LinkedIn](https://www.linkedin.com/in/vasiliki-netsiou) · [Portfolio](https://netsiou.dev)
