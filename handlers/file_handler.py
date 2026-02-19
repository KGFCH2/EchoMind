"""File and folder handler"""
import re
import subprocess
import os
from config.settings import OS, LOCATION_MAP
from utils.voice_io import speak
from utils.logger import log_interaction

def handle_file_opening(command):
    """Handle file and folder opening commands"""
    if not re.search(r'\b(open|show)\b.*(pdf|file|document|documents|folder|downloads|pictures|music|videos|explorer)', command, re.IGNORECASE):
        return False
    
    command_lower = command.lower()
    
    # Determine which location to open
    location = None
    for loc_key in LOCATION_MAP:
        if loc_key in command_lower:
            location = LOCATION_MAP[loc_key]
            break
    
    # Default to opening file explorer
    if not location:
        if OS == "windows":
            location = os.path.expanduser('~\\Documents')
        else:
            location = os.path.expanduser('~')
    
    try:
        if OS == "windows":
            subprocess.Popen(["explorer", location])
        elif OS == "darwin":
            subprocess.Popen(["open", location])
        elif OS == "linux":
            subprocess.Popen(["nautilus", location])
        
        speak(f"Opening file explorer")
        log_interaction(command, "Opened file explorer", source="local")
        return True
    except Exception as e:
        speak("Sorry, I couldn't open the file explorer.")
        print(f"Error: {e}")
        return False
