"""Weather handler"""
import re
from config.settings import WEATHER_CITY_BLACKLIST
from utils.voice_io import speak, listen
from utils.weather import get_weather
from utils.logger import log_interaction

def handle_weather(command):
    """Handle weather commands with multi-pattern detection"""
    
    # Skip if this is a browser search command (has browser keyword + on/in separator)
    if re.search(r'\b(on|in)\b.*\b(chrome|firefox|edge|google|browser)\b', command, re.IGNORECASE):
        return False
    
    # Check for weather-related keywords
    weather_match = re.search(r'\b(weather|forecast|temperature)\b.*\b(in|of|at|for|around)\s+(\w+)\b', command, re.IGNORECASE) or \
                   re.search(r'\b(\w+)\s+(weather|forecast|temperature|current weather)\b', command, re.IGNORECASE) or \
                   re.search(r'\b(weather|forecast|temperature|current weather)\b', command, re.IGNORECASE)
    
    if not weather_match:
        return False
    
    # Try to extract city name from the command
    city = None
    
    # Pattern 1: "weather of/in/for CITY"
    match1 = re.search(r'\b(weather|forecast|temperature)\b.*\b(?:of|in|at|for|around)\s+(\w+)\b', command, re.IGNORECASE)
    if match1:
        city = match1.group(2)
    
    # Pattern 2: "CITY weather/forecast" (but not "current")
    if not city:
        match2 = re.search(r'\b(\w+)\s+(weather|forecast|temperature|current weather)\b', command, re.IGNORECASE)
        if match2:
            potential_city = match2.group(1).lower()
            if potential_city not in WEATHER_CITY_BLACKLIST:
                city = match2.group(1)
    
    # If no city found, ask user
    if not city:
        speak("Which city would you like the weather for?")
        city = listen()
    
    if city:
        weather_info = get_weather(city)
        speak(weather_info)
        log_interaction(command, weather_info, source="local")
        return True
    
    return False
