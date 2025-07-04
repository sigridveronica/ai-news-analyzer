import os
import sys
import tempfile
import streamlit as st
import pandas as pd

# Add 'src' to Python path so we can import main.py
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from main import run_pipeline  # ✅ src/main.py must have this function
st.title("AI-Powered Investing News Analyzer")

# 1. API Key Input
st.subheader("🔐 API Keys")
openai_api_key = st.text_input("OpenAI API Key", type="password")
tavily_api_key = st.text_input("Tavily API Key", type="password")

# 2. Topic Input
st.subheader("📰 Topics of Interest")
topics_data = []

with st.form("topics_form"):
    topic_count = st.number_input("How many topics do you want to analyze?", min_value=1, max_value=10, step=1, value=1)
    
    for i in range(topic_count):
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input(f"Topic {i+1}", key=f"topic_{i}")
        with col2:
            timespan = st.number_input(f"Timespan (days) for Topic {i+1}", min_value=1, max_value=30, value=7, key=f"days_{i}")
        topics_data.append({"topic": topic, "timespan_days": timespan})

    submitted = st.form_submit_button("Analyze Topics")


if submitted:
    if not openai_api_key or not tavily_api_key or not all([td['topic'] for td in topics_data]):
        st.warning("Please fill in all fields.")
    else:
        # Save inputs
        os.environ["OPENAI_API_KEY"] = openai_api_key.strip()
        os.environ["TAVILY_API_KEY"] = tavily_api_key.strip()

        # Create temp CSV for topics
        df = pd.DataFrame(topics_data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_csv:
            df.to_csv(tmp_csv.name, index=False)
            csv_path = tmp_csv.name

        with st.spinner("Running analysis..."):
            output_path = run_pipeline(csv_path, tavily_api_key)

        if os.path.exists(output_path):
            st.success("✅ Analysis complete!")
            with open(output_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
                st.download_button("📥 Download HTML Report", html_content, file_name="news_report.html", mime="text/html")
                st.components.v1.html(html_content, height=600, scrolling=True)
        else:
            st.error("❌ Something went wrong during the analysis.")

