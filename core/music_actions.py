import webbrowser
from urllib.parse import quote_plus


def play_on_youtube_music(query: str) -> bool:
    """
    Abre YouTube Music buscando la canción, artista o playlist indicada.
    """
    if not query:
        return False

    encoded_query = quote_plus(query)
    url = f"https://music.youtube.com/search?q={encoded_query}"

    webbrowser.open(url)
    return True