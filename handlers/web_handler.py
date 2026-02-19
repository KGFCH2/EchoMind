"""Web search and browser handlers"""
import re
import subprocess
import webbrowser
import time
from config.settings import OS, WEBSITE_MAP
from utils.voice_io import speak, listen
from utils.logger import log_interaction

def handle_web_search(command):
    """Handle web search commands"""
    url = f"https://www.google.com/search?q={command}"
    webbrowser.open(url)
    speak(f"Searching for {command} on Google")
    log_interaction(command, f"Search opened: {command}", source="local")


def handle_whatsapp_web(command):
    """Handle WhatsApp Web commands"""
    command_lower = command.lower()
    
    # Check if it's a WhatsApp command
    if not re.search(r'\b(open|launch|start)\b.*\bwhatsapp\b', command_lower):
        return False
    
    # Check if user wants to message someone
    if re.search(r'\bmessage\b|\btext\b|\bsend\b', command_lower):
        # Extract contact name if possible
        message_match = re.search(r'(?:message|text|send)\s+(?:to\s+)?(.+?)(?:\s+(?:on|via))?$', command_lower)
        contact = message_match.group(1).strip() if message_match else None
        
        try:
            # Open WhatsApp Web
            whatsapp_url = "https://web.whatsapp.com/"
            if OS == "windows":
                subprocess.Popen(["cmd", "/c", f"start chrome {whatsapp_url}"], shell=True)
            elif OS == "darwin":
                subprocess.Popen(["open", "-a", "Google Chrome", whatsapp_url])
            elif OS == "linux":
                subprocess.Popen(["google-chrome", whatsapp_url])
            
            speak("Opening WhatsApp Web")
            
            if contact:
                speak(f"To message {contact}, please select their chat from WhatsApp and type your message.")
                log_interaction(command, f"Opened WhatsApp Web for {contact}", source="local")
            else:
                log_interaction(command, "Opened WhatsApp Web", source="local")
            
            return True
        except Exception as e:
            speak("Sorry, I couldn't open WhatsApp Web.")
            print(f"WhatsApp error: {e}")
            return False
    else:
        # Just open WhatsApp Web
        try:
            whatsapp_url = "https://web.whatsapp.com/"
            if OS == "windows":
                subprocess.Popen(["cmd", "/c", f"start chrome {whatsapp_url}"], shell=True)
            elif OS == "darwin":
                subprocess.Popen(["open", "-a", "Google Chrome", whatsapp_url])
            elif OS == "linux":
                subprocess.Popen(["google-chrome", whatsapp_url])
            
            speak("Opening WhatsApp Web")
            log_interaction(command, "Opened WhatsApp Web", source="local")
            return True
        except Exception as e:
            speak("Sorry, I couldn't open WhatsApp Web.")
            return False

def handle_browser_search(command):
    """Handle browser-based search and opening"""
    # Pattern: check for browser mention with "on" or "in" separator
    # More flexible to catch various search intents
    if not re.search(r'\b(on|in)\b.*\b(chrome|firefox|edge|google|browser)\b', command, re.IGNORECASE):
        return False
    
    # Make sure it's not a pure weather query (has "weather" without action words)
    if re.search(r'\bweather\b', command, re.IGNORECASE) and not re.search(r'\b(search|open|look|find|check|get)\b', command, re.IGNORECASE):
        return False
    
    command_lower = command.lower()
    
    # Extract browser
    browser = None
    browser_name = None
    if "chrome" in command_lower or ("google" in command_lower and ("api" in command_lower or "search" in command_lower)):
        browser = "chrome"
        browser_name = "chrome"
    elif "firefox" in command_lower:
        browser = "firefox"
        browser_name = "firefox"
    elif "edge" in command_lower:
        browser = "edge"
        browser_name = "microsoft edge"
    
    # Extract search query more robustly
    query = None
    if " on " in command_lower:
        parts = command_lower.split(" on ")
        if len(parts) >= 2:
            query_part = parts[0].strip()
            # Remove leading action words
            for prefix in ["open ", "search ", "look for ", "find ", "get ", "check "]:
                if query_part.startswith(prefix):
                    query_part = query_part[len(prefix):].strip()
                    break
            query = query_part
    elif " in " in command_lower:
        parts = command_lower.split(" in ")
        if len(parts) >= 2:
            query_part = parts[0].strip()
            # Remove leading action words
            for prefix in ["open ", "search ", "look for ", "find ", "get ", "check "]:
                if query_part.startswith(prefix):
                    query_part = query_part[len(prefix):].strip()
                    break
            query = query_part
    
    if browser and query:
        try:
            # Check if query is a URL or a search term
            if query.startswith("http://") or query.startswith("https://") or "." in query:
                url = query if query.startswith("http") else f"https://{query}"
            else:
                url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            
            # Launch the browser
            if browser == "chrome":
                if OS == "windows":
                    subprocess.Popen(["cmd", "/c", f"start chrome {url}"], shell=True)
                elif OS == "darwin":
                    subprocess.Popen(["open", "-a", "Google Chrome", url])
                elif OS == "linux":
                    subprocess.Popen(["google-chrome", url])
            elif browser == "firefox":
                if OS == "windows":
                    subprocess.Popen(["cmd", "/c", f"start firefox {url}"], shell=True)
                elif OS == "darwin":
                    subprocess.Popen(["open", "-a", "Firefox", url])
                elif OS == "linux":
                    subprocess.Popen(["firefox", url])
            elif browser == "edge":
                if OS == "windows":
                    subprocess.Popen(["cmd", "/c", f"start msedge {url}"], shell=True)
                elif OS == "darwin":
                    subprocess.Popen(["open", "-a", "Microsoft Edge", url])
                elif OS == "linux":
                    subprocess.Popen(["microsoft-edge", url])
            
            speak(f"Searching for {query} on {browser_name}")
            log_interaction(command, f"Opened {query} on {browser_name}", source="local")
            return True
        except Exception as e:
            speak("Sorry, I couldn't open that in the browser.")
            print(f"Browser opening error: {e}")
            return False
    
    return False

def handle_website_opening(command):
    """Handle website opening commands"""
    if not re.search(r'\b(open|visit|go to)\b\s+(youtube|wikipedia|reddit|github|facebook|twitter|instagram|gmail|google\.com|stack\s*overflow)', command, re.IGNORECASE):
        return False
    
    command_lower = command.lower()
    
    # Find which website was mentioned
    website = None
    for site_key in WEBSITE_MAP:
        if site_key in command_lower:
            website = site_key
            break
    
    if website:
        try:
            url = WEBSITE_MAP[website]
            if OS == "windows":
                subprocess.Popen(["cmd", "/c", f"start chrome {url}"], shell=True)
            elif OS == "darwin":
                subprocess.Popen(["open", "-a", "Google Chrome", url])
            elif OS == "linux":
                subprocess.Popen(["google-chrome", url])
            speak(f"Opening {website}")
            log_interaction(command, f"Opened {website}", source="local")
            return True
        except Exception as e:
            speak(f"Sorry, I couldn't open {website}.")
            print(f"Error: {e}")
            return False
    
    return False
