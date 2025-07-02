value_investing/
├── data/               ← ✅ Markdown files go here
├── html/               ← ✅ Generated HTML files go here
├── src/                ← ✅ All your Python code lives here
│   ├── main.py
│   ├── md_html.py
│   ├── news_analysis.py
│   ├── image_search.py
├── investing_topics.csv
├── .env

| File               | Role                                                                |
| ------------------ | ------------------------------------------------------------------- |
| `main.py`          | Orchestrates everything: load CSV, generate MD, call HTML converter |
| `md_html.py`       | Converts `.md` → `.html` with styling                               |
| `image_search.py`  | Fetches Unsplash image + credit based on smart keywords             |
| `news_analysis.py` | Searches news + generates value investing memo from articles        |


