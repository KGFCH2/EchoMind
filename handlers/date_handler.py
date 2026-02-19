"""Date handler"""
import re
from utils.voice_io import speak
from utils.time_utils import get_date
from utils.logger import log_interaction

def handle_date(command):
    """Handle date commands"""
    if re.search(r'\b(date|what date|what is the date|what\'s the date|today\'s date|what day is it|what is the day|tell me the date|current date|current day)\b', command, re.IGNORECASE):
        date_info = get_date()
        speak(f"Today's date is {date_info}")
        log_interaction(command, f"Today's date is {date_info}", source="local")
        return True
    return False
