"""Application settings and constants"""
import os
import platform
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Detect operating system
OS = platform.system().lower()

# API Keys from environment
API_KEY = os.getenv("OPENWEATHER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not set. Gemini features will be disabled until you set this environment variable.")

# Common applications dictionary (Windows-focused)
COMMON_APPS = {
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "paint": "mspaint",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "ppt": "powerpnt",
    "chrome": "chrome",
    "firefox": "firefox",
    "edge": "msedge",
    "browser": "chrome",
    "file explorer": "explorer",
    "explorer": "explorer",
    "command prompt": "cmd",
    "cmd": "cmd",
    "powershell": "powershell",
    "settings": "start ms-settings:",
    "control panel": "control",
    "task manager": "taskmgr",
    "camera": "start microsoft.windows.camera:",
    "photos": "start microsoft.windows.photos:",
    "store": "start ms-windows-store:",
    "google": "chrome",
    "google chrome": "chrome",
}

# Website mapping
WEBSITE_MAP = {
    'youtube': 'https://www.youtube.com',
    'wikipedia': 'https://www.wikipedia.com',
    'reddit': 'https://www.reddit.com',
    'github': 'https://www.github.com',
    'facebook': 'https://www.facebook.com',
    'twitter': 'https://www.twitter.com',
    'instagram': 'https://www.instagram.com',
    'gmail': 'https://mail.google.com',
    'google': 'https://www.google.com',
    'stackoverflow': 'https://stackoverflow.com',
    'stack overflow': 'https://stackoverflow.com',
}

# File locations mapping
LOCATION_MAP = {
    'downloads': os.path.expanduser('~\\Downloads'),
    'documents': os.path.expanduser('~\\Documents'),
    'pictures': os.path.expanduser('~\\Pictures'),
    'music': os.path.expanduser('~\\Music'),
    'videos': os.path.expanduser('~\\Videos'),
    'desktop': os.path.expanduser('~\\Desktop'),
}

# Process names for app closing
PROCESS_NAMES = {
    "camera": ["microsoft.windows.camera", "camera"],
    "chrome": ["chrome.exe", "chrome"],
    "google": ["chrome.exe", "chrome"],
    "firefox": ["firefox.exe", "firefox"],
    "edge": ["msedge.exe", "msedge"],
    "browser": ["chrome.exe", "firefox.exe", "msedge.exe"],
    "youtube": ["chrome.exe", "firefox.exe", "msedge.exe"],
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "word": ["winword.exe"],
    "excel": ["excel.exe"],
    "powerpoint": ["powerpnt.exe"],
    "ppt": ["powerpnt.exe"],
}

# Connector words to clean from app commands
CONNECTOR_WORDS = ["and ", "with ", "to ", "inside ", "then ", "also "]

# City extraction blacklist for weather
WEATHER_CITY_BLACKLIST = ("current", "what", "tell", "give", "show", "get", "find")

# Exit keywords
EXIT_KEYWORDS = ["exit", "quit", "stop", "bye", "goodbye", "terminate"]

# Thank you keywords
THANK_YOU_KEYWORDS = ["thank you", "thanks", "thankyou", "thx", "thank"]
