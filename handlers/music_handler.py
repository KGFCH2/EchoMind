"""Music playback handler - Search and play songs on YouTube"""
import re
import subprocess
import webbrowser
import urllib.parse
from config.settings import OS
from utils.voice_io import speak
from utils.logger import log_interaction


def _find_youtube_video_url(song_query):
    """
    Try to extract video ID and build direct play URL
    This searches YouTube and constructs a direct link to the first result
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # Search YouTube
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(song_query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(search_url, headers=headers, timeout=5)
            if response.status_code == 200:
                # Try to extract first video ID
                match = re.search(r'"videoId":"([^"]+)"', response.text)
                if match:
                    video_id = match.group(1)
                    return f"https://www.youtube.com/watch?v={video_id}"
        except:
            pass
        
        return None
    except:
        return None


def _open_video_url(video_url):
    """Open a video URL directly"""
    try:
        if OS == "windows":
            # Try Chrome first, then Edge, then default browser
            browsers = [
                ["cmd", "/c", f"start chrome {video_url}"],
                ["cmd", "/c", f"start msedge {video_url}"],
            ]
            
            for browser_cmd in browsers:
                try:
                    subprocess.Popen(browser_cmd, shell=True)
                    return True
                except:
                    continue
            
            # Fallback to default browser
            webbrowser.open(video_url)
            return True
            
        elif OS == "darwin":  # macOS
            subprocess.Popen(["open", "-a", "Google Chrome", video_url])
            return True
            
        elif OS == "linux":
            subprocess.Popen(["google-chrome", video_url])
            return True
    except:
        return False


def handle_play_music(command):
    """
    Handle play music commands
    Patterns:
    - "play <song_name>"
    - "play <song_name> by <artist>"
    - "play music <song_name>"
    
    Now attempts to play the first video directly instead of just searching
    """
    # Check if command contains play keyword
    if not re.search(r'\bplay\b', command, re.IGNORECASE):
        return False
    
    command_lower = command.lower().strip()
    
    # Don't handle if it's explicitly for YouTube (handled by handle_play_on_youtube)
    if "on youtube" in command_lower or "on you tube" in command_lower:
        return False
    
    # Extract the song query
    song_query = None
    
    # Pattern 1: "play <song>"
    if command_lower.startswith("play "):
        song_query = command_lower[5:].strip()
    # Pattern 2: "play music <song>"
    elif "play music" in command_lower:
        song_query = command_lower.replace("play music", "", 1).strip()
    # Pattern 3: Other variations with "play"
    elif " play " in command_lower:
        # Extract after "play"
        match = re.search(r'\bplay\s+(.+)', command_lower)
        if match:
            song_query = match.group(1).strip()
    
    # If we found a song query, search it on YouTube and play
    if song_query:
        try:
            speak(f"Playing {song_query}")
            
            # Try to find direct video URL
            video_url = _find_youtube_video_url(song_query)
            
            if video_url:
                # Open the video directly
                _open_video_url(video_url)
                log_interaction(command, f"YouTube play (direct): {song_query}", source="music")
            else:
                # Fallback to search results if direct link fails
                youtube_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(song_query)}"
                _open_video_url(youtube_url)
                log_interaction(command, f"YouTube search (fallback): {song_query}", source="music")
            
            return True
        except Exception as e:
            speak("Sorry, I couldn't play the music on YouTube.")
            print(f"Music play error: {e}")
            log_interaction(command, f"Music error: {e}", source="music")
            return False
    
    return False


def handle_play_on_youtube(command):
    """
    Alternative handler for explicit YouTube play commands
    Patterns:
    - "play <song> on youtube"
    - "youtube play <song>"
    
    Now attempts to play the first video directly
    """
    if not re.search(r'\b(play|youtube)\b.*\byoutube\b', command, re.IGNORECASE):
        if not re.search(r'\byoutube\s+play\b', command, re.IGNORECASE):
            return False
    
    command_lower = command.lower().strip()
    
    # Extract song query
    song_query = None
    
    # Pattern 1: "play <song> on youtube"
    if "on youtube" in command_lower or "on you tube" in command_lower:
        match = re.search(r'play\s+(.+?)\s+on\s+you\s*tube', command_lower)
        if match:
            song_query = match.group(1).strip()
    # Pattern 2: "youtube play <song>"
    elif command_lower.startswith("youtube play"):
        song_query = command_lower[12:].strip()
    
    if song_query:
        try:
            speak(f"Playing {song_query} on YouTube")
            
            # Try to find direct video URL
            video_url = _find_youtube_video_url(song_query)
            
            if video_url:
                # Open the video directly
                _open_video_url(video_url)
                log_interaction(command, f"YouTube play (direct): {song_query}", source="music")
            else:
                # Fallback to search results
                youtube_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(song_query)}"
                _open_video_url(youtube_url)
                log_interaction(command, f"YouTube search (fallback): {song_query}", source="music")
            
            return True
        except Exception as e:
            speak("Sorry, I couldn't play the music on YouTube.")
            print(f"YouTube play error: {e}")
            log_interaction(command, f"YouTube play error: {e}", source="music")
            return False
    
    return False
