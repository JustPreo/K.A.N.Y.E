import subprocess
import webbrowser
from urllib.parse import quote_plus


def search_youtube_first_video(query: str) -> str | None:
    """
    Busca el primer resultado de YouTube usando yt-dlp.
    Devuelve el ID del video.
    """
    if not query:
        return None

    try:
        command = [
            "python",
            "-m",
            "yt_dlp",
            f"ytsearch1:{query}",
            "--print",
            "%(id)s",
            "--no-playlist"
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=20
        )

        video_id = result.stdout.strip().splitlines()[0]

        if video_id:
            return video_id

        return None

    except Exception as error:
        print(f"K.A.N.Y.E.: Error buscando canción: {error}")
        return None


def play_on_youtube_music(query: str) -> bool:
    """
    Busca el primer resultado y abre directamente YouTube Music.
    """
    if not query:
        return False

    video_id = search_youtube_first_video(query)

    if not video_id:
        # Fallback: si falla yt-dlp, abre la búsqueda normal.
        encoded_query = quote_plus(query)
        url = f"https://music.youtube.com/search?q={encoded_query}"
        webbrowser.open(url)
        return True

    url = f"https://music.youtube.com/watch?v={video_id}"
    webbrowser.open(url)
    return True