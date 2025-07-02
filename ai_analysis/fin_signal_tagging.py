import re

FINANCIAL_KEYWORDS = [
    "IPO", "Series A", "Series B", "funding", "acquisition", "merger",
    "partnership", "earnings", "revenue", "valuation", "investment",
    "raise", "round", "debt", "exit", "seed", "growth", "MoM", "ARR", "burn rate"
]

def extract_signals(text):
    found = []
    for kw in FINANCIAL_KEYWORDS:
        pattern = r"\b" + re.escape(kw.lower()) + r"\b"
        if re.search(pattern, text.lower()):
            found.append(kw)
    return list(set(found))
