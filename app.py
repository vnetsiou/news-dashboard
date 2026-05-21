import threading
from apscheduler.schedulers.background import BackgroundScheduler
from collector import run as collect

# Run collector immediately on startup, then every 6 hours
collect()

scheduler = BackgroundScheduler()
scheduler.add_job(collect, "interval", hours=6)
scheduler.start()

# Dashboard runs via streamlit (see Procfile)
