import os
import sys
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

import pandas as pd

from news_analysis import fetch_deep_news, generate_value_investor_report
from image_search import search_unsplash_image
from md_html import convert_md_folder_to_html
from csv_utils import detect_changes

# Add external path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXTERNAL_PATH = os.path.join(BASE_DIR, "external")
if EXTERNAL_PATH not in sys.path:
    sys.path.append(EXTERNAL_PATH)

# Load .env variables
load_dotenv()

# Folder setup
DATA_DIR = os.path.join(BASE_DIR, "data")
HTML_DIR = os.path.join(BASE_DIR, "html")
CSV_PATH = os.path.join(BASE_DIR, "investing_topics.csv")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(HTML_DIR, exist_ok=True)

def build_metrics_box(topic, num_articles):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""
> Topic: `{topic}`
> Articles Collected: `{num_articles}`
> Generated: `{now}`
"""

def run_analysis(csv_path):
    current_df = pd.read_csv(csv_path)
    prev_path = os.path.join(BASE_DIR, "investing_topics_prev.csv")

    if os.path.exists(prev_path):
        previous_df = pd.read_csv(prev_path)
        changed_df = detect_changes(current_df, previous_df)
        if changed_df.empty:
            st.info("✅ No new topics detected. Skipping reprocessing.")
            return []
    else:
        changed_df = current_df

    generated_files = []

    for _, row in changed_df.iterrows():
        topic = row.get("topic")
        timespan = row.get("timespan_days", 7)
        st.write(f"🔍 Searching: {topic} ({timespan} days)")

        news = fetch_deep_news(topic, timespan)
        if not news:
            st.warning(f"⚠️ No news found for: {topic}")
            continue

        report_body = generate_value_investor_report(topic, news)
        image_url, image_credit = search_unsplash_image(topic)
        metrics_md = build_metrics_box(topic, len(news))
        full_md = metrics_md + report_body

        base_filename = f"{topic.replace(' ', '_').lower()}_{datetime.now().strftime('%Y-%m-%d')}"
        filename = base_filename + ".md"
        filepath = os.path.join(DATA_DIR, filename)

        counter = 1
        while os.path.exists(filepath):
            filename = f"{base_filename}_{counter}.md"
            filepath = os.path.join(DATA_DIR, filename)
            counter += 1

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_md)

        generated_files.append(filepath)

    current_df.to_csv(prev_path, index=False)
    return generated_files

# === Streamlit UI ===
st.set_page_config(page_title="AI4Finance Investment Analyzer", layout="centered")
st.title("📈 AI4Finance Investment News Analyzer")

if st.button("🚀 Run Investment Report Generator"):
    with st.spinner("Running analysis..."):
        generated = run_analysis(CSV_PATH)
        convert_md_folder_to_html(DATA_DIR, HTML_DIR)

    if generated:
        st.success(f"✅ Generated {len(generated)} report(s).")
        for file in os.listdir(HTML_DIR):
            if file.endswith(".html"):
                html_path = os.path.join(HTML_DIR, file)
                st.markdown(f"[📰 View Report: {file}](./html/{file})", unsafe_allow_html=True)
    else:
        st.info("No new reports created.")

st.divider()
st.markdown("You can edit `investing_topics.csv` to add new topics and re-run the analysis.")
