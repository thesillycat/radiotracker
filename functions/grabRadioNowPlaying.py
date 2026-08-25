import requests
import json
import re

combinedKeys = ["streamtitle", "np", "current_song", "songtitle", "cue_title", "text"]
splitPattern = re.compile(r"\s-\s|\s–\s|:\s")


def _split_combined(value):
    """Try to split a combined 'Artist - Title' style string into a dict."""
    if not isinstance(value, str) or not value.strip():
        return None
    parts = splitPattern.split(value, maxsplit=1)
    if len(parts) == 2:
        artist, title = parts[0].strip(), parts[1].strip()
        if artist and title:
            return {"title": title, "artist": artist}
    return None


def _find_song(data, depth=0, max_depth=6):
    if depth > max_depth:
        return None

    if isinstance(data, dict):
        if isinstance(data.get("song"), str):
            result = _split_combined(data["song"])
            if result:
                return result

        if isinstance(data.get("title"), str) and isinstance(data.get("artist"), str):
            if data["title"].strip() and data["artist"].strip():
                return {"title": data["title"].strip(), "artist": data["artist"].strip()}

        if isinstance(data.get("artist"), str) and isinstance(data.get("track"), str):
            if data["artist"].strip() and data["track"].strip():
                return {"title": data["track"].strip(), "artist": data["artist"].strip()}

        for key in combinedKeys:
            if isinstance(data.get(key), str) and data[key].strip():
                result = _split_combined(data[key])
                if result:
                    return result

        for value in data.values():
            if isinstance(value, (dict, list)):
                found = _find_song(value, depth + 1, max_depth)
                if found:
                    return found

    elif isinstance(data, list):
        for item in data:
            found = _find_song(item, depth + 1, max_depth)
            if found:
                return found

    return None


def grabRadioNowPlaying(radioStation):
    """Returns a dict {'title': ..., 'artist': ...} or None if nothing found."""
    with open("data/collectedRadioStations.json") as f:
        fileJson = json.loads(f.read())

    if radioStation not in fileJson:
        return None

    nowPlayingResp = requests.get(fileJson[radioStation]["nowPlayingEndpoint"])
    try:
        payload = nowPlayingResp.json()
    except ValueError:
        return None

    return _find_song(payload)


def grabAllNowPlaying():
    with open("data/collectedRadioStations.json") as f:
        fileJson = json.loads(f.read())
    nowPlayingDict = {}
    for station in fileJson:
        nowPlayingResp = requests.get(fileJson[station]["nowPlayingEndpoint"])
        try:
            payload = nowPlayingResp.json()
        except ValueError:
            payload = {}

        nowPlayingDict[station] = _find_song(payload)
    return nowPlayingDict