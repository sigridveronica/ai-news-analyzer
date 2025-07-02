# tavily.py
import requests

class TavilyClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.tavily.com/search"

    def search(
        self,
        query: str,
        search_depth: str = "advanced",
        topic: str = "news",
        days: int = 7,
        max_results: int = 10,
        include_answer: bool = False,
        include_raw_content: bool = False
    ):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "query": query,
            "search_depth": search_depth,
            "topic": topic,
            "days": days,
            "max_results": max_results,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content
        }

        response = requests.post(self.api_url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Tavily API error: {response.status_code} - {response.text}")

        return response.json()
