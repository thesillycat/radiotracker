from flask import Flask, render_template, request
import sqlite3
from functions.sendToDatabase import DEFAULT_DB_PATH

app = Flask(__name__)


def get_stations():
    conn = sqlite3.connect(DEFAULT_DB_PATH)
    rows = conn.execute("SELECT DISTINCT station_name FROM nowplaying ORDER BY station_name").fetchall()
    conn.close()
    return [r[0] for r in rows]


def get_records(station=None, limit=100):
    conn = sqlite3.connect(DEFAULT_DB_PATH)
    conn.row_factory = sqlite3.Row
    if station:
        rows = conn.execute(
            "SELECT * FROM nowplaying WHERE station_name = ? ORDER BY id DESC LIMIT ?",
            (station, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM nowplaying ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    conn.close()
    return rows


def get_library(station=None):
    """Returns unique songs (title + artist), deduplicated, with play count and last played time."""
    conn = sqlite3.connect(DEFAULT_DB_PATH)
    conn.row_factory = sqlite3.Row

    baseQuery = """
        SELECT
            title,
            artist,
            album,
            image_url,
            COUNT(*) AS play_count,
            MAX(played_at) AS last_played
        FROM nowplaying
        WHERE title IS NOT NULL AND artist IS NOT NULL
    """

    params = ()
    if station:
        baseQuery += " AND station_name = ?"
        params = (station,)

    baseQuery += """
        GROUP BY LOWER(title), LOWER(artist)
        ORDER BY last_played DESC
    """

    rows = conn.execute(baseQuery, params).fetchall()
    conn.close()
    return rows


@app.route("/")
def index():
    selectedStation = request.args.get("station")
    stations = get_stations()
    records = get_records(selectedStation)
    return render_template("index.html", stations=stations, records=records, selectedStation=selectedStation)


@app.route("/library")
def library():
    selectedStation = request.args.get("station")
    stations = get_stations()
    songs = get_library(selectedStation)
    return render_template("library.html", stations=stations, songs=songs, selectedStation=selectedStation)