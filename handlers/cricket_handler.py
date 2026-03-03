"""Cricket score handler"""
import re
import requests
from config.settings import CRICKETDATA_API_KEY
from utils.voice_io import speak, listen
from utils.logger import log_interaction

def handle_cricket_score(command):
    """Handle commands for real-time cricket scores"""
    
    # Check for cricket-related keywords
    cricket_match = re.search(r'\b(cricket score|live score|cricket match|match score|cricket|t20|world cup|ipl)\b', command, re.IGNORECASE)
    
    if not cricket_match:
        return False
        
    if not CRICKETDATA_API_KEY:
        speak("Cricket API key is not configured. Please add CRICKETDATA_API_KEY to your environment variables.")
        log_interaction(command, "Cricket API key not configured", source="local")
        return True

    speak("Let me check the live cricket scores.")
    
    try:
        url = f"https://api.cricketdata.org/v1/cricScore?apikey={CRICKETDATA_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "success" or not data.get("data"):
            speak("Sorry, I couldn't find any live cricket matches at the moment.")
            log_interaction(command, "No live matches found", source="local")
            return True
            
        matches = data.get("data", [])
        live_matches = [m for m in matches if m.get("t1s") or m.get("t2s") or m.get("status") != "Match not started"]
        
        if not live_matches:
            # Let general AI handle queries about past/future matches if no live/recent matches found in API
            return False
            
        # Get the first live match details
        match = live_matches[0]
        match_name = match.get("name", "Unknown Match")
        status = match.get("status", "")
        t1_score = match.get("t1s", "")
        t2_score = match.get("t2s", "")
        
        score_text = f"In the match between {match_name}. "
        if t1_score:
            score_text += f"{match.get('t1', 'Team 1')} is at {t1_score}. "
        if t2_score:
            score_text += f"{match.get('t2', 'Team 2')} is at {t2_score}. "
        
        if not t1_score and not t2_score:
            score_text += f"The current status is: {status}."
        elif status:
            score_text += f"Status: {status}."
            
        speak(score_text)
        log_interaction(command, score_text, source="local")
        return True
        
    except Exception as e:
        speak("Sorry, I encountered an error while fetching the cricket score.")
        log_interaction(command, f"Error fetching cricket score: {str(e)}", source="local")
        return True

    return False
