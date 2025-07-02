#uses HuggingFace pipeline to classify text sentiment (positive, neutral, negative) with FinBERT.

from transformers import pipeline

# Load FinBERT financial sentiment pipeline
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="ProsusAI/finbert",
    top_k=None
)

def analyze_sentiment(text):
    try:
        result = sentiment_pipeline(text[:512])[0]  # limit size for tokenizer
        return result["label"].lower(), round(result["score"], 3)
    except Exception as e:
        return "error", 0.0
