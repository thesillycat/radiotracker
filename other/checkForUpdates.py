import requests
import os
from colorama import init, Fore, Style

init(autoreset=True)

VERSION_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "VERSION"
)

def getCurrentVersion():
    try:
        with open(VERSION_FILE) as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"

def checkVersion():
    repoVersion = requests.get("https://raw.githubusercontent.com/thesillycat/radiotracker/refs/heads/main/VERSION").text.strip()
    if repoVersion != getCurrentVersion():
        print(f"{Fore.YELLOW}Update available: {repoVersion} (current: {getCurrentVersion()}){Style.RESET_ALL}")
        print(f"{Fore.WHITE}Run: git pull or reclone the repository to update.{Style.RESET_ALL}")