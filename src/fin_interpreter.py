# src/fin_interpreter.py

#Also loads FinBERT via HuggingFace, manually tokenizes and gives basic logic to infer "Invest", "Avoid", or "Watch" based on sentiment + keywords.
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict
import sys
import os
from tavily import TavilyClient
import sys
import os

# ✅ Correct path to FinGPT
FINGPT_PATH = "/Users/sigridveronica/Desktop/Investing/external/FinGPT"
sys.path.append(FINGPT_PATH)


# Define the base path one level up from the current file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "external", "FinGPT"))
sys.path.append(os.path.join(BASE_DIR, "external/FinGPT"))



# Add FinGPT path to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "external", "FinGPT")))

# Add project root to sys.path to access ai_analysis
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)


# Load FinBERT (FinNLP)
sentiment_model = "ProsusAI/finbert"
tokenizer = AutoTokenizer.from_pretrained(sentiment_model)
model = AutoModelForSequenceClassification.from_pretrained(sentiment_model, use_safetensors=True)
fin_sentiment = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

from ai_analysis.fin_signal_tagging import extract_signals

def analyze_article(text: str) -> Dict:
    try:
        result = fin_sentiment(text[:512])[0]
        sentiment = result['label'].lower()
        confidence = round(result['score'], 3)

        signals = extract_signals(text)  # ← ADD THIS

        if sentiment == "positive" and any(sig in signals for sig in ["funding", "acquisition", "Series A"]):
            decision = "Invest"
        elif sentiment == "neutral":
            decision = "Watch"
        else:
            decision = "Avoid"

        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "investment_decision": decision,
            "signals": signals  # ← ADD THIS TOO
        }

    except Exception as e:
        return {
            "sentiment": "error",
            "confidence": 0,
            "investment_decision": "unknown",
            "signals": []
        }
