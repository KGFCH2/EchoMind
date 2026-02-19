"""Time handler"""
import re
from utils.voice_io import speak
from utils.time_utils import get_time
from utils.logger import log_interaction

def handle_time(command):
    """Handle time commands"""
    if re.search(r'\b(what time|what is the time|what\'s the time|current time|tell me the time|time now)\b', command, re.IGNORECASE):
        time_str = get_time()
        speak(f"The current time is {time_str}")
        log_interaction(command, f"The current time is {time_str}", source="local")
        return True
    return False
