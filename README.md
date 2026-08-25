# RadioTracker

RadioTracker polls one or more internet radio stations for now playing data, enriches it with track metadata (album, cover art, duration) from Deezer, and stores every play in a local SQLite database. A built-in web viewer lets you browse recent plays or a deduplicated library of every song a station has played.

![recentsongs](githubimgs/1.png)
![library](githubimgs/2library.png)

## Features

- **Polls multiple stations on a schedule** — configurable interval, runs continuously in the background
- **Handles inconsistent station APIs** — a recursive parser finds title/artist data regardless of how a station's JSON is shaped (AzuraCast, Radio.co, Icecast, combined "Artist - Title" strings, and more)
- **Enriches tracks via Deezer** — pulls album name, duration, track ID, and cover art automatically
- **Skips duplicate entries** — won't log the same song twice while it's still playing, but correctly logs it again if it comes back around later
- **Web viewer** — browse recent plays per station or view a deduplicated library with play counts, all from a local browser tab

## Get started

Configure your install at `config.json` before running.

```
git clone https://github.com/thesillycat/radiotracker
pip install -r requirements.txt
python3 run.py
```

## Configuration

**`config.json`**

```json
{
    "COMMENT": "Fetch interval is in seconds.",
    "fetchInterval": "60",
    "host": "0.0.0.0",
    "port": "5000"
}
```

| Key             | Description                                      |
|-----------------|---------------------------------------------------|
| `fetchInterval` | How often (in seconds) to poll all stations       |
| `host`          | Host the web viewer binds to                      |
| `port`          | Port the web viewer runs on                        |

**`data/collectedRadioStations.json`**

Add each station you want to track, keyed by a short name, with its now-playing API endpoint:

```json
{
    "azuracastTestRadio": {
        "name": "Azuracast Test Radio",
        "url": "https://azuracast.com/",
        "stream": "https://demo.azuracast.com/listen/azuratest_radio/radio.mp3",
        "type": "azuracast",
        "nowPlayingEndpoint": "https://demo.azuracast.com/api/nowplaying/1"
    }
}
```
