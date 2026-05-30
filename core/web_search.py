import webbrowser
from urllib.parse import quote_plus


def search_google(query: str) -> bool:
    if not query:
        return False

    encoded_query = quote_plus(query)
    url = f"https://www.google.com/search?q={encoded_query}"

    webbrowser.open(url)
    return True