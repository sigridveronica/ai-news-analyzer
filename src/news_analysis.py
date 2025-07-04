import os
import csv
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
import requests
from dotenv import load_dotenv
from fin_interpreter import analyze_article
from tavily import TavilyClient

# === Load environment or passed keys ===
load_dotenv()
OPENAI_KEY = os.environ.get("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
TAVILY_KEY = os.environ.get("TAVILY_API_KEY") or os.getenv("TAVILY_KEY")

# === Initialize Tavily Client ===
tavily_client = TavilyClient(api_key=TAVILY_KEY)

# === Get OpenAI client when needed ===
def get_llm():
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("OPENAI_API_KEY not found.")
    return ChatOpenAI(model_name="gpt-4.1", openai_api_key=openai_key)

# === Related Terms ===
def get_related_terms(topic):
    llm = get_llm()
    prompt = f"What are 5 closely related financial or industry terms to '{topic}'?"
    response = llm.invoke(prompt)
    return response.content.split(",")

def tavily_search(query, days, max_results=10):
    api_key = os.getenv("TAVILY_KEY")
    url = "https://api.tavily.com/search"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "query": query,
        "search_depth": "advanced",
        "topic": "news",
        "days": int(days),
        "max_results": max_results,
        "include_answer": False,
        "include_raw_content": False
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# === Smart News Search ===
def fetch_deep_news(topic, days):
    all_results = []
    seen_urls = set()

    base_queries = [
        topic,
        f"{topic} AND startup",
        f"{topic} AND acquisition OR merger OR funding",
        f"{topic} AND CEO OR executive OR leadership",
        f"{topic} AND venture capital OR Series A OR Series B",
        f"{topic} AND government grant OR approval OR contract",
        f"{topic} AND underrated OR small-cap OR micro-cap"
    ]

    investor_queries = [
        f"{topic} AND BlackRock OR Vanguard OR SoftBank",
        f"{topic} AND Elon Musk OR Sam Altman OR Peter Thiel",
        f"{topic} AND Berkshire Hathaway OR Warren Buffett",
        f"{topic} AND institutional investor OR hedge fund",
    ]

    related_terms = get_related_terms(topic)
    synonym_queries = [f"{term} AND {kw}" for term in related_terms for kw in ["startup", "funding", "merger", "acquisition"]]

    all_queries = base_queries + investor_queries + synonym_queries

    for query in all_queries:
        try:
            print(f"🔍 Tavily query: {query}")
            response = requests.post(
                url="https://api.tavily.com/search",
                headers={
                    "Authorization": f"Bearer {TAVILY_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "query": query,
                    "search_depth": "advanced",
                    "topic": "news",
                    "days": int(days),
                    "max_results": 10,
                    "include_answer": False,
                    "include_raw_content": False
                }
            )

            if response.status_code != 200:
                print(f"⚠️ Tavily API error: {response.status_code} - {response.text}")
                continue

            for item in response.json().get("results", []):
                url = item.get("url")
                content = item.get("content", "") or item.get("summary", "") or item.get("title", "")
                if url and url not in seen_urls and len(content) > 150:
                    all_results.append({
                        "title": item.get("title"),
                        "url": url,
                        "content": content
                    })
                    seen_urls.add(url)

        except Exception as e:
            print(f"⚠️ Tavily request failed for query '{query}': {e}")

    print(f"📰 Total articles collected: {len(all_results)}")
    return all_results

# === Generate Markdown Report ===
def generate_value_investor_report(topic, news_results, max_articles=20, max_chars_per_article=400):
    news_results = news_results[:max_articles]

    for item in news_results:
        result = analyze_article(item["content"])
        item["fin_sentiment"] = result.get("sentiment", "neutral")
        item["fin_confidence"] = result.get("confidence", 0.0)
        item["investment_decision"] = result.get("investment_decision", "Watch")

    article_summary = "".join(
        f"- **{item['title']}**: {item['content'][:max_chars_per_article]}... "
        f"(Sentiment: {item['fin_sentiment'].title()}, Confidence: {item['fin_confidence']:.2f}, "
        f"Decision: {item['investment_decision']}) [link]({item['url']})\n"
        for item in news_results
    )

    prompt = PromptTemplate.from_template("""
You're a highly focused value investor. Analyze this week's news on "{Topic}".

Your goal is to uncover:
- Meaningful events (e.g., CEO joining a startup, insider buys, big-name partnerships)
- Startups or small caps that may signal undervalued opportunity
- Connections to key individuals or institutions (e.g., Elon Musk investing, Sam Altman joining)
- Companies with strong fundamentals: low P/E, low P/B, high ROE, recent IPOs, moats, or high free cash flow

### News
{ArticleSummaries}

Write a markdown memo with:
1. **Key Value Signals**
2. **Stocks or Startups to Watch**
3. **What Smart Money Might Be Acting On**
4. **References**
5. **Investment Hypothesis**

Include context and macroeconomic/regulatory angles. Add an intro on sentiment and market trends for the week.
""")

    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate(prompt=prompt)
    ])
    prompt_value = chat_prompt.format_prompt(
        Topic=topic,
        ArticleSummaries=article_summary
    ).to_messages()

    llm = get_llm()
    result = llm.invoke(prompt_value)
    return result.content
