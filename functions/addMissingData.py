import re
import requests

DEEZER_SEARCH_URL = "https://api.deezer.com/search"
FEAT_PATTERN = re.compile(r"\s*[\(\[]\s*(feat\.?|ft\.?|with)\s+.*?[\)\]]", re.IGNORECASE)


def _clean_title(title):
    if not title:
        return title
    cleaned = FEAT_PATTERN.sub("", title)
    return re.sub(r"\s+", " ", cleaned).strip()


def addMissingData(title, artist):
    if not title or not artist:
        return None
    cleanTitle = _clean_title(title)
    query = f'track:"{cleanTitle}" artist:"{artist}"'
    resp = requests.get(DEEZER_SEARCH_URL, params={"q": query})
    try:
        results = resp.json().get("data", [])
    except ValueError:
        return None
    if not results:
        query = f"{cleanTitle} {artist}"
        resp = requests.get(DEEZER_SEARCH_URL, params={"q": query})
        try:
            results = resp.json().get("data", [])
        except ValueError:
            return None

    if not results:
        return None
    track = results[0]
    albumInfo = track.get("album", {})
    return {
        "album": albumInfo.get("title"),
        "duration": track.get("duration"),
        "track_id": track.get("id"),
        "image_url": albumInfo.get("cover_xl")
                     or albumInfo.get("cover_big")
                     or albumInfo.get("cover_medium")
                     or albumInfo.get("cover"),
    }