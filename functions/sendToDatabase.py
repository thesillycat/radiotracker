import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from functions.addMissingData import addMissingData


DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "radiotracker.db",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ensure_database(db_path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS nowplaying (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_name TEXT NOT NULL,
            title TEXT,
            artist TEXT,
            album TEXT,
            duration INTEGER,
            track_id TEXT,
            image_url TEXT,
            played_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    return conn


def get_last_record(station_name: str, db_path: str = DEFAULT_DB_PATH) -> Optional[sqlite3.Row]:
    """Returns the most recent record for a station, or None if there are no records yet."""
    conn = _ensure_database(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            """
            SELECT * FROM nowplaying
            WHERE station_name = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (station_name,),
        ).fetchone()
        return row
    finally:
        conn.close()


def is_same_as_last(station_name: str, title: str, artist: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    last = get_last_record(station_name, db_path)
    if last is None:
        return False

    lastTitle = (last["title"] or "").strip().lower()
    lastArtist = (last["artist"] or "").strip().lower()
    currentTitle = (title or "").strip().lower()
    currentArtist = (artist or "").strip().lower()

    return lastTitle == currentTitle and lastArtist == currentArtist


def sendToDatabase(
    station_name: str,
    title: Optional[str] = None,
    artist: Optional[str] = None,
    album: Optional[str] = None,
    duration: Optional[int] = None,
    track_id: Optional[str] = None,
    image_url: Optional[str] = None,
    played_at: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH,
) -> int:
    if not station_name:
        raise ValueError("station_name is required")

    normalized_played_at = played_at or _utc_now_iso()

    conn = _ensure_database(db_path)
    try:
        cursor = conn.execute(
            """
            INSERT INTO nowplaying (
                station_name,
                title,
                artist,
                album,
                duration,
                track_id,
                image_url,
                played_at,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                station_name,
                title,
                artist,
                album,
                duration,
                track_id,
                image_url,
                normalized_played_at,
                _utc_now_iso(),
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)
    finally:
        conn.close()