"""Greeting handler"""
import re
from utils.voice_io import speak
from utils.logger import log_interaction

def handle_greeting(command):
    """Handle greeting commands"""
    if re.search(r'\b(hello|hi|hey|greetings)\b', command, re.IGNORECASE):
        speak("Hello! How can I help you?")
        log_interaction(command, "Hello! How can I help you?", source="local")
        return True
    return False
