from functions.grabRadioNowPlaying import grabRadioNowPlaying
from functions.sendToDatabase import DEFAULT_DB_PATH, sendToDatabase
from functions.addMissingData import addMissingData
from other.checkForUpdates import *
from viewer import app as viewer_app
from datetime import datetime, timezone
from colorama import init, Fore, Style
import json
import time
import threading

init(autoreset=True)
checkVersion()


def log_info(message):
    print(f"{Fore.CYAN}[RadioTracker]{Style.RESET_ALL} {message}")


def log_success(message):
    print(f"{Fore.GREEN}[RadioTracker]{Style.RESET_ALL} {message}")


def log_warn(message):
    print(f"{Fore.YELLOW}[RadioTracker]{Style.RESET_ALL} {message}")


def log_error(message):
    print(f"{Fore.RED}[RadioTracker]{Style.RESET_ALL} {message}")


def print_intro():
    banner = rf"""{Fore.MAGENTA}{Style.BRIGHT}
  ____           _ _       _____               _
 |  _ \ __ _  __| (_) ___ |_   _| __ __ _  ___| | _____ _ __
 | |_) / _` |/ _` | |/ _ \  | || '__/ _` |/ __| |/ / _ \ '__|
 |  _ < (_| | (_| | | (_) | | || | | (_| | (__|   <  __/ |
 |_| \_\__,_|\__,_|_|\___/  |_||_|  \__,_|\___|_|\_\___|_|
{Style.RESET_ALL}"""
    print(banner)
    print(f"{Fore.WHITE}{Style.DIM}       Now Playing Tracker — starting up...{Style.RESET_ALL}\n")
    time.sleep(2)


def load_config():
    with open("config.json") as f:
        return json.load(f)


def load_stations():
    with open("data/collectedRadioStations.json") as f:
        return json.load(f)


def process_station(stationName):
    nowPlayingInfo = grabRadioNowPlaying(stationName)

    if not nowPlayingInfo:
        log_warn(f"Cannot find now playing information for {stationName}.")
        return

    title = nowPlayingInfo["title"]
    artist = nowPlayingInfo["artist"]

    log_info(f"Song currently playing on {Fore.YELLOW}{stationName}{Style.RESET_ALL}: "
              f"{Fore.WHITE}{Style.BRIGHT}{title}{Style.RESET_ALL} by "
              f"{Fore.WHITE}{Style.BRIGHT}{artist}{Style.RESET_ALL}")

    deezerInfo = addMissingData(title, artist)
    album = deezerInfo["album"] if deezerInfo else None
    duration = deezerInfo["duration"] if deezerInfo else None
    track_id = deezerInfo["track_id"] if deezerInfo else None
    image_url = deezerInfo["image_url"] if deezerInfo else None
    played_at = datetime.now(timezone.utc).isoformat()

    record_id = sendToDatabase(
        station_name=stationName,
        title=title,
        artist=artist,
        album=album,
        duration=duration,
        track_id=track_id,
        image_url=image_url,
        played_at=played_at,
        db_path=DEFAULT_DB_PATH,
    )

    log_success(json.dumps({"station": stationName, "record_id": record_id}))


def run_once():
    stations = load_stations()
    for stationName in stations:
        try:
            process_station(stationName)
        except Exception as e:
            log_error(f"Error processing {stationName}: {e}")


def poll_loop():
    config = load_config()
    fetchInterval = int(config["fetchInterval"])

    log_info(f"Polling every {Fore.YELLOW}{fetchInterval}{Style.RESET_ALL} seconds...")

    while True:
        run_once()
        log_info(f"Sleeping for {fetchInterval} seconds...\n")
        time.sleep(fetchInterval)


def main():
    print_intro()

    pollThread = threading.Thread(target=poll_loop, daemon=True)
    pollThread.start()

    config = load_config()
    log_success(f"Starting web viewer at {Fore.CYAN}http://{config['host']}:{config['port']}{Style.RESET_ALL}")
    viewer_app.run(debug=False, host=config["host"], port=int(config["port"]), use_reloader=False)


if __name__ == "__main__":
    main()