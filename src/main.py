import os
import sys
from datetime import datetime
from dotenv import load_dotenv

from news_analysis import load_csv, fetch_deep_news, generate_value_investor_report
from image_search import search_unsplash_image
from md_html import convert_md_folder_to_html

import pandas as pd
from csv_utils import detect_changes


# Adds the absolute path of /external to your module path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXTERNAL_PATH = os.path.join(BASE_DIR, "external")
if EXTERNAL_PATH not in sys.path:
    sys.path.append(EXTERNAL_PATH)

# Load .env
load_dotenv()

# === Base Folder Setup ===
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # one level up from src/
DATA_DIR = os.path.join(BASE_DIR, "data")
HTML_DIR = os.path.join(BASE_DIR, "html")
CSV_PATH = os.path.join(BASE_DIR, "investing_topics.csv")



# Ensure output folders exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(HTML_DIR, exist_ok=True)

# === Metrics Block ===
def build_metrics_box(topic, num_articles):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""
> Topic: `{topic}`
> Articles Collected: `{num_articles}`
> Generated: `{now}`
>
"""

# === Main Logic ===
def run_value_investing_analysis(csv_path):
    current_df = pd.read_csv(csv_path)

    prev_path = os.path.join(BASE_DIR, "investing_topics_prev.csv")
    if os.path.exists(prev_path):
        previous_df = pd.read_csv(prev_path)
        changed_df = detect_changes(current_df, previous_df)
        if changed_df.empty:
            print("✅ No changes detected. Skipping processing.")
            return
    else:
        changed_df = current_df

    for _, row in changed_df.iterrows():
        topic = row.get("topic")
        timespan = row.get("timespan_days", 7)
        print(f"\n🔍 Processing: {topic} ({timespan} days)")

        news = fetch_deep_news(topic, timespan)
        if not news:
            print(f"⚠️ No news found for: {topic}")
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

    print(f"✅ Markdown saved to: {DATA_DIR}")
    current_df.to_csv(prev_path, index=False)  # Save current as previous for next run

#convert_md_folder_to_html(DATA_DIR, HTML_DIR)
#print(f"🌐 All reports converted to HTML at: {HTML_DIR}")



# === Run ===
if __name__ == "__main__":
    run_value_investing_analysis(CSV_PATH)
    convert_md_folder_to_html(DATA_DIR, HTML_DIR)
    print(f"🌐 All reports converted to HTML at: {HTML_DIR}")
