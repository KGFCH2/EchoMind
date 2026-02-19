"""Thank you handler"""
import re
from config.settings import THANK_YOU_KEYWORDS
from utils.voice_io import speak
from utils.logger import log_interaction

def handle_thank_you(command):
    """Handle thank you commands"""
    if any(phrase in command for phrase in THANK_YOU_KEYWORDS):
        speak("You are most welcome.... Happy to help you")
        log_interaction(command, "You are most welcome.... Happy to help you", source="local")
        return True
    return False
