import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_unsplash_keywords(title, num_keywords=2):
    prompt = f"""
Extract {num_keywords} distinct, concise, visually-relevant keywords for Unsplash image search from this article title.

Format: space-separated, lowercase. No punctuation.
Title: {title}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Keyword extraction failed: {e}")
        return title  # fallback

def search_unsplash_image(title):
    keywords = extract_unsplash_keywords(title)
    try:
        response = requests.get(
            "https://api.unsplash.com/search/photos",
            headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
            params={"query": keywords, "orientation": "landscape", "per_page": 1}
        )
        data = response.json()
        if data.get("results"):
            photo = data["results"][0]
            image_url = photo["urls"]["regular"]
            author_name = photo["user"]["name"]
            author_username = photo["user"]["username"]
            author_link = f"https://unsplash.com/@{author_username}"

            # 💡 Return clean HTML credit
            image_credit_html = (
                f'Photo by <a href="{author_link}" target="_blank">{author_name}</a> '
                f'on <a href="https://unsplash.com" target="_blank">Unsplash</a>'
            )
            return image_url, image_credit_html

    except Exception as e:
        print(f"❌ Unsplash fetch failed: {e}")

    return "https://via.placeholder.com/1281x721?text=No+Image+Found", "Image unavailable"
