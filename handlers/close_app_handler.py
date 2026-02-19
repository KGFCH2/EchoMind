"""Application closing handler"""
import re
import subprocess
import time
import psutil
from config.settings import OS, PROCESS_NAMES
from utils.voice_io import speak
from utils.logger import log_interaction

# Track opened applications by user command
OPENED_APPS = {}  # {app_name: process_name}
OPENED_TABS = {}  # {browser: [tab_names]}


def register_opened_app(app_name, process_name):
    """Register an app that was opened by the assistant"""
    OPENED_APPS[app_name.lower()] = process_name.lower()


def register_opened_tab(browser_name, tab_name):
    """Register a tab that was opened in a browser"""
    browser_lower = browser_name.lower()
    if browser_lower not in OPENED_TABS:
        OPENED_TABS[browser_lower] = []
    OPENED_TABS[browser_lower].append(tab_name.lower())


def handle_app_closing(command):
    """Handle application closing commands
    
    Supports:
    - "close powerpoint" → closes PowerPoint
    - "close youtube tab" → closes only the YouTube tab in browser
    - "close youtube in edge" → closes YouTube tab specifically in Edge
    - "close chrome" → closes entire Chrome browser
    - "youtube tab" → closes the YouTube tab (implied close)
    - "close microsoft edge" → closes Microsoft Edge application (multi-word app names)
    - "close the chat gpt tab" → closes ChatGPT tab (multi-word tab names)
    - "close the first tab on chrome" → closes first tab (using Ctrl+W)
    - "close the fast youtube tab" → closes YouTube tab (ignores adjectives like "fast")
    - "close the current tab" → closes current active tab (uses Ctrl+W)
    - "close this tab" → closes current active tab (uses Ctrl+W)
    """
    command_lower = command.lower().strip()
    
    # EXCLUSION: Don't process exit/quit keywords - let exit handler handle them
    exit_keywords = ['exit', 'terminate', 'stop yourself', 'quit', 'goodbye']
    if any(keyword in command_lower for keyword in exit_keywords):
        return False  # Don't process - let exit handler handle this
    
    # PATTERN 0: Close current/active tab - "close the current tab" or "close this tab"
    if re.search(r'(?:close|shut|kill)\s+(?:the\s+)?(?:current|this|active)\s+tab', command_lower):
        speak("Closing current tab")
        _close_tab_with_hotkey(command)
        log_interaction(command, "Closed current tab using Ctrl+W", source="local")
        return True
    
    # Check for explicit close/shut/kill commands
    has_close_word = re.search(r'\b(close|shut|kill|terminate|stop)\b', command_lower)
    
    # Check if user is asking about tabs (more specific: "tab" not followed by "le" or "let")
    # This prevents matching "table", "tablet", "tablespoon", etc.
    has_tab_keyword = re.search(r'\btab(?:s)?\b(?!le|let)', command_lower)
    
    # If no close word and no tab keyword, don't process this command
    if not has_close_word and not has_tab_keyword:
        return False
    
    # Ordinals and adjectives to filter out
    ordinals = r"first|second|third|fourth|fifth|last"
    adjectives = r"fast|slow|open|active|new|old|main|primary|secondary"
    
    # PATTERN 1: close [ordinal] tab on [browser]
    # e.g., "close the second tab on google chrome" → Use Ctrl+W
    ordinal_tab_browser = re.search(
        r'(?:close|shut|kill)?\s+(?:the\s+)?(?:' + ordinals + r')\s+tab\s+(?:on|in)\s+([a-z\s]+?)(?:\s+browser)?$',
        command_lower
    )
    if ordinal_tab_browser:
        browser_name = ordinal_tab_browser.group(1).strip()
        speak("Closing tab using keyboard shortcut")
        _close_tab_with_hotkey(command)
        log_interaction(command, "Closed tab using Ctrl+W", source="local")
        return True
    
    # PATTERN 2: close [adjective]* [ordinal]* [tab_name] tab
    # Filter out both adjectives AND ordinals from capture group
    # e.g., "close the fast youtube tab" → Captures "youtube" (not "fast")
    # e.g., "close the first youtube tab" → Captures "youtube" (not "first")
    adjective_tab = re.search(
        r'(?:close|shut|kill)?\s+(?:the\s+)?(?:\b(?:' + adjectives + r')\s+)*(?:(?:' + ordinals + r')\s+)*([a-z]+(?:\s+[a-z]+)*?)\s+tab',
        command_lower
    )
    if adjective_tab:
        target = adjective_tab.group(1).strip()
        # Verify it's not just an adjective or ordinal
        excluded_words = ['fast', 'slow', 'open', 'active', 'new', 'old', 'main', 'primary', 'secondary',
                          'first', 'second', 'third', 'fourth', 'fifth', 'last']
        if target.lower() not in excluded_words:
            # Extract browser if mentioned with on/in
            browser_match = re.search(r'(?:on|in)\s+([a-z\s]+?)(?:\s+browser)?$', command_lower)
            browser_name = browser_match.group(1).strip() if browser_match else None
            
            # Check if target is an app, not a tab
            apps = ("chrome", "firefox", "edge", "microsoft edge", "powerpoint", "word", "excel", 
                   "notepad", "calculator", "discord", "settings")
            if target.lower() in apps:
                return _close_application_instance(target.lower(), command)
            else:
                return _close_tab_or_website(target, browser_name, command)
    
    # PATTERN 3: IMPLICIT tab close - just "[name] tab" without close word
    # e.g., "youtube tab" → Close youtube tab
    if has_tab_keyword and not has_close_word:
        implicit_tab = re.search(r'^([a-z]+(?:\s+[a-z]+)*?)\s+tab$', command_lower)
        if implicit_tab:
            target = implicit_tab.group(1).strip()
            # Verify it's not an excluded word
            excluded_words = ['fast', 'slow', 'open', 'active', 'new', 'old', 'main', 'primary', 'secondary',
                              'first', 'second', 'third', 'fourth', 'fifth', 'last']
            if target.lower() not in excluded_words:
                apps = ("chrome", "firefox", "edge", "microsoft edge", "powerpoint", "word", "excel", 
                       "notepad", "calculator", "discord", "settings")
                if target.lower() in apps:
                    return _close_application_instance(target.lower(), command)
                else:
                    return _close_tab_or_website(target, None, command)
    
    # PATTERN 4: close [app_name] (without tab keyword - application close)
    # e.g., "close microsoft edge" → Close entire application
    if has_close_word and not has_tab_keyword:
        app_match = re.search(r'(?:close|shut|kill|terminate|stop)\s+(?:the\s+)?([a-z\s]+?)(?:\s+browser)?$', command_lower)
        if app_match:
            target = app_match.group(1).strip()
            apps = ("chrome", "firefox", "edge", "microsoft edge", "powerpoint", "word", "excel", 
                   "notepad", "calculator", "discord", "settings")
            if target.lower() in apps:
                return _close_application_instance(target.lower(), command)
    
    return False




def _close_tab_with_hotkey(command):
    """Close the active tab using keyboard shortcut (Ctrl+W)
    
    This is used for closing ordinal tabs like "close the first tab"
    """
    try:
        import pyautogui
        
        # Send Ctrl+W to close the current/active tab
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(0.5)
        
        log_interaction(command, "Closed active tab using Ctrl+W", source="local")
        return True
        
    except ImportError:
        try:
            import keyboard
            keyboard.press_and_release('ctrl+w')
            time.sleep(0.5)
            log_interaction(command, "Closed active tab using keyboard", source="local")
            return True
        except:
            speak("Please close the tab manually")
            return False
    except Exception as e:
        speak("Could not close the tab. Please close it manually.")
        print(f"Error: {e}")
        return False


def _close_tab_or_website(tab_name, browser_name, command):
    """Close a specific tab without closing the entire browser
    
    This sends Ctrl+W to close the active tab
    """
    try:
        import pyautogui
        
        # Focus on the browser window first (try to find it)
        if browser_name:
            browser_lower = browser_name.lower()
            if "chrome" in browser_lower:
                # Try to activate Chrome window
                try:
                    if OS == "windows":
                        subprocess.run(["tasklist", "/FI", "IMAGENAME eq chrome.exe"], capture_output=True)
                except:
                    pass
            elif "edge" in browser_lower or "microsoft" in browser_lower:
                try:
                    if OS == "windows":
                        subprocess.run(["tasklist", "/FI", "IMAGENAME eq msedge.exe"], capture_output=True)
                except:
                    pass
            elif "firefox" in browser_lower:
                try:
                    if OS == "windows":
                        subprocess.run(["tasklist", "/FI", "IMAGENAME eq firefox.exe"], capture_output=True)
                except:
                    pass
        
        # Send Ctrl+W to close the current tab (works if tab is active)
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(0.5)
        
        speak(f"Closing {tab_name} tab")
        log_interaction(command, f"Closed {tab_name} tab using Ctrl+W", source="local")
        return True
        
    except ImportError:
        # pyautogui not available, try using keyboard module or ask user
        try:
            import keyboard
            keyboard.press_and_release('ctrl+w')
            time.sleep(0.5)
            speak(f"Closing {tab_name} tab")
            log_interaction(command, f"Closed {tab_name} tab", source="local")
            return True
        except:
            # Ask user to click on the tab and then close
            speak(f"Please click on the {tab_name} tab and I'll close it for you")
            return False
    except Exception as e:
        speak(f"Could not close the {tab_name} tab. Please close it manually.")
        print(f"Error: {e}")
        return False


def _close_application_instance(app_name, command):
    """Close a specific application instance
    
    For applications like:
    - PowerPoint
    - Word
    - Excel
    - Discord
    - Settings
    - Browsers (Chrome, Firefox, Edge)
    """
    app_lower = app_name.lower().strip()
    
    # Map app names to process names
    app_process_map = {
        "powerpoint": ["POWERPNT.exe", "powerpnt.exe"],
        "word": ["WINWORD.exe", "winword.exe"],
        "excel": ["EXCEL.exe", "excel.exe"],
        "notepad": ["notepad.exe"],
        "calculator": ["calc.exe"],
        "discord": ["Discord.exe", "discord.exe"],
        "chrome": ["chrome.exe"],
        "firefox": ["firefox.exe"],
        "edge": ["msedge.exe"],
        "settings": ["SystemSettings.exe"],
    }
    
    # Try to find and close the application
    if app_lower in app_process_map:
        process_names = app_process_map[app_lower]
        closed_count = 0
        
        try:
            if OS == "windows":
                for proc_name in process_names:
                    try:
                        # Use taskkill to close the application
                        result = subprocess.run(
                            ["taskkill", "/IM", proc_name, "/F"],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        
                        if result.returncode == 0:
                            closed_count += 1
                            print(f"Closed: {proc_name}")
                    except Exception as e:
                        print(f"Could not close {proc_name}: {e}")
            
            elif OS == "darwin":  # macOS
                for proc_name in process_names:
                    # Remove .exe if present for macOS
                    proc_name_mac = proc_name.replace('.exe', '')
                    try:
                        subprocess.run(
                            ["killall", "-9", proc_name_mac],
                            capture_output=True,
                            timeout=5
                        )
                        closed_count += 1
                    except:
                        pass
            
            elif OS == "linux":
                for proc_name in process_names:
                    proc_name_linux = proc_name.replace('.exe', '').lower()
                    try:
                        subprocess.run(
                            ["killall", "-9", proc_name_linux],
                            capture_output=True,
                            timeout=5
                        )
                        closed_count += 1
                    except:
                        pass
            
            if closed_count > 0:
                speak(f"Closing {app_lower}")
                log_interaction(command, f"Closed {app_lower} application", source="local")
                return True
            else:
                speak(f"{app_lower.capitalize()} is not currently running or could not be closed")
                log_interaction(command, f"{app_lower} not found or already closed", source="local")
                return True
        
        except Exception as e:
            speak(f"Sorry, I couldn't close {app_lower}.")
            print(f"Error closing app: {e}")
            return False
    
    else:
        # Unknown application
        speak(f"I don't know how to close {app_lower}.")
        return False
