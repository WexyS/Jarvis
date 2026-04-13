"""
Ultron Action: web_search — DuckDuckGo ile web araması.
"""

from duckduckgo_search import DDGS


def run(parameters: dict, **kwargs) -> str: # type: ignore
    """DuckDuckGo ile web araması yapar."""
    query = (parameters or {}).get("query", "").strip() # type: ignore
    if not query:
        return "Lütfen bir arama sorgusu belirtin."

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5)) # type: ignore
        if not results:
            return f"'{query}' için sonuç bulunamadı."

        parts = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            body = r.get("body", "")[:200]
            url = r.get("href", "")
            if title and body:
                parts.append(f"{i}. {title}\n   {body}\n   {url}") # type: ignore
        return "\n\n".join(parts) # type: ignore
    except Exception as e:
        return f"Arama hatası: {e}"
