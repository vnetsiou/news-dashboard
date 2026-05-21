import os
import psycopg2
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

st.set_page_config(page_title="News Sentiment Dashboard", page_icon="📰", layout="wide")

from collector import run as collect_news

st.title("📰 News Sentiment Dashboard")
st.caption("Real-time sentiment analysis of news headlines powered by a custom RoBERTa API.")

col_title, col_btn = st.columns([4, 1])
with col_btn:
    if st.button("🔄 Refresh News", use_container_width=True):
        with st.spinner("Fetching latest news..."):
            collect_news()
        st.cache_data.clear()
        st.success("Done!")
        st.rerun()


@st.cache_data(ttl=300)
def load_data():
    conn = psycopg2.connect(DATABASE_URL)
    df = pd.read_sql("SELECT * FROM articles ORDER BY fetched_at DESC", conn)
    conn.close()
    return df


try:
    df = load_data()
except Exception as e:
    st.warning(f"No data yet — run `collector.py` first. ({e})")
    st.stop()

if df.empty:
    st.warning("No data yet — run `collector.py` first.")
    st.stop()

# --- Filters ---
col1, col2 = st.columns(2)
with col1:
    topics = ["All"] + sorted(df["topic"].unique().tolist())
    selected_topic = st.selectbox("Topic", topics)
with col2:
    sentiments = ["All"] + sorted(df["sentiment"].unique().tolist())
    selected_sentiment = st.selectbox("Sentiment", sentiments)

filtered = df.copy()
if selected_topic != "All":
    filtered = filtered[filtered["topic"] == selected_topic]
if selected_sentiment != "All":
    filtered = filtered[filtered["sentiment"] == selected_sentiment]

# --- KPIs ---
st.divider()
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Articles", len(filtered))
k2.metric("Positive", len(filtered[filtered["sentiment"] == "positive"]))
k3.metric("Negative", len(filtered[filtered["sentiment"] == "negative"]))
k4.metric("Neutral", len(filtered[filtered["sentiment"] == "neutral"]))

# --- Charts ---
st.divider()
c1, c2 = st.columns(2)

colors = {"positive": "#00BC91", "negative": "#ef4444", "neutral": "#94a3b8"}

with c1:
    st.subheader("Sentiment Distribution")
    pie = filtered["sentiment"].value_counts().reset_index()
    pie.columns = ["sentiment", "count"]
    fig = px.pie(pie, names="sentiment", values="count",
                 color="sentiment", color_discrete_map=colors, hole=0.4)
    fig.update_layout(margin=dict(t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Sentiment by Topic")
    bar = filtered.groupby(["topic", "sentiment"]).size().reset_index(name="count")
    fig2 = px.bar(bar, x="topic", y="count", color="sentiment",
                  color_discrete_map=colors, barmode="group")
    fig2.update_layout(margin=dict(t=0, b=0))
    st.plotly_chart(fig2, use_container_width=True)

# --- Headlines by Sentiment ---
st.divider()
st.subheader("Latest Headlines")

col_pos, col_neu, col_neg = st.columns(3)

positive = filtered[filtered["sentiment"] == "positive"].head(15)
neutral  = filtered[filtered["sentiment"] == "neutral"].head(15)
negative = filtered[filtered["sentiment"] == "negative"].head(15)

with col_pos:
    st.markdown("### 😊 Positive")
    for _, row in positive.iterrows():
        conf = f"{row['confidence']*100:.1f}%"
        st.markdown(f"**{row['title']}**  \n`{row['source']}` · `{row['topic']}` · {conf}")
        st.divider()

with col_neu:
    st.markdown("### 😐 Neutral")
    for _, row in neutral.iterrows():
        conf = f"{row['confidence']*100:.1f}%"
        st.markdown(f"**{row['title']}**  \n`{row['source']}` · `{row['topic']}` · {conf}")
        st.divider()

with col_neg:
    st.markdown("### 😤 Negative")
    for _, row in negative.iterrows():
        conf = f"{row['confidence']*100:.1f}%"
        st.markdown(f"**{row['title']}**  \n`{row['source']}` · `{row['topic']}` · {conf}")
        st.divider()
