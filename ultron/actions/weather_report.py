"""
Ultron Action: weather_report — Hava durumu bilgisi.
"""

import webbrowser
from urllib.parse import quote_plus


def run(parameters: dict, **kwargs) -> str: # type: ignore
    """Hava durumu sayfasını tarayıcıda açar."""
    city = (parameters or {}).get("city", "").strip() # type: ignore
    if not city:
        return "Lütfen bir şehir adı belirtin."

    search_query = f"weather in {city}"
    encoded_query = quote_plus(search_query)
    url = f"https://www.google.com/search?q={encoded_query}"

    try:
        webbrowser.open(url)
        return f"{city} için hava durumu tarayıcıda açılıyor."
    except Exception:
        return "Tarayıcı açılamadı."
