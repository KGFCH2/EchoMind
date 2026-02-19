"""Application handler"""
import re
import subprocess
import time
import os
import sys
import winreg
from config.settings import OS, COMMON_APPS
from utils.voice_io import speak, listen, speak_stream
from utils.text_processing import clean_connector_words
from utils.logger import log_interaction


def find_installed_apps_windows():
    """Find all installed applications on Windows by scanning registry"""
    apps = {}
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    
    try:
        for path in registry_paths:
            try:
                reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(reg_key, i)
                        subkey = winreg.OpenKey(reg_key, subkey_name)
                        
                        try:
                            app_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            app_path = None
                            
                            # Try to find executable path
                            try:
                                app_path = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                            except:
                                pass
                            
                            # Clean up app name
                            app_name_clean = app_name.lower().strip()
                            if app_name_clean and len(app_name_clean) > 1:
                                apps[app_name_clean] = {
                                    'name': app_name,
                                    'path': app_path
                                }
                        finally:
                            winreg.CloseKey(subkey)
                        i += 1
                    except WindowsError:
                        break
                winreg.CloseKey(reg_key)
            except:
                pass
    except Exception as e:
        print(f"Error scanning registry: {e}")
    
    return apps


def find_installed_apps_linux():
    """Find installed applications on Linux"""
    apps = {}
    try:
        # Search in standard locations
        common_paths = [
            '/usr/share/applications',
            '/usr/local/share/applications',
            os.path.expanduser('~/.local/share/applications')
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                for file in os.listdir(path):
                    if file.endswith('.desktop'):
                        app_name = file.replace('.desktop', '').lower()
                        apps[app_name] = {'name': app_name, 'path': os.path.join(path, file)}
    except Exception as e:
        print(f"Error finding Linux apps: {e}")
    
    return apps


def find_installed_apps():
    """Find all installed apps based on OS"""
    if OS == "windows":
        return find_installed_apps_windows()
    elif OS == "linux":
        return find_installed_apps_linux()
    else:
        # macOS and others will use default approach
        return {}

def handle_app_opening(command):
    """Handle application opening commands"""
    if not re.search(r'\b(open|launch|start)\b', command, re.IGNORECASE):
        return False
    
    app = None
    remaining_text = None
    command_lower = command.lower()
    
    # Extract app name from command
    for prefix in ["open ", "launch ", "start "]:
        if command_lower.startswith(prefix):
            remainder = command[len(prefix):].strip()
            app_words = remainder.split()
            
            if len(app_words) >= 2:
                first_word = app_words[0].lower()
                if "microsoft" in first_word or first_word == "ms":
                    app = " ".join(app_words[:2])
                    remaining_text = " ".join(app_words[2:]) if len(app_words) > 2 else None
                elif first_word in COMMON_APPS:
                    app = first_word
                    remaining_text = " ".join(app_words[1:]) if len(app_words) > 1 else None
                else:
                    app = first_word
                    remaining_text = " ".join(app_words[1:]) if len(app_words) > 1 else None
            else:
                app = remainder
                remaining_text = None
            break
    
    # Clean up connector words from remaining text
    if remaining_text:
        remaining_text = clean_connector_words(remaining_text)
    
    if not app:
        speak("Which app would you like to open?")
        app = listen()
    
    if app:
        app_lower = app.lower().strip()
        app_clean = app_lower.replace("microsoft ", "").replace("ms ", "").replace(" app", "").strip()
        
        if app_clean in ("google", "google chrome"):
            app_clean = "chrome"
        
        # Check if it's a common app first
        if app_clean in COMMON_APPS:
            launch_cmd = COMMON_APPS[app_clean]
            try:
                if OS == "windows":
                    if launch_cmd.startswith("start "):
                        subprocess.run(["cmd", "/c", launch_cmd], shell=True)
                    else:
                        subprocess.run(["cmd", "/c", "start", launch_cmd], shell=True)
                elif OS == "darwin":
                    subprocess.run(["open", "-a", launch_cmd], capture_output=True)
                elif OS == "linux":
                    subprocess.run(["xdg-open", launch_cmd], capture_output=True)
                
                speak(f"Opening {app}")
                log_interaction(command, f"Opening {app}", source="local")
                
                # If there's remaining text, process it with Gemini
                if remaining_text and remaining_text.strip():
                    _process_remaining_text(remaining_text)
                return True
            except Exception as e:
                speak("Sorry, I couldn't open that app.")
                return False
        else:
            # NEW APPROACH: Use Windows Search to find and open the app
            if OS == "windows":
                return _open_app_with_windows_search(app, command, remaining_text)
            else:
                # For non-Windows, use the old approach
                return _open_app_legacy(app, app_clean, command, remaining_text)
    
    return False


def _open_app_with_windows_search(app, command, remaining_text):
    """Open app using Windows Search (Windows key + S)
    
    This method:
    1. Opens Windows Search (Win + S)
    2. Types the app name
    3. Waits for search results
    4. Presses Enter to open the first result
    """
    try:
        import pyautogui
        import time as time_module
        
        speak(f"Searching for {app} on your device")
        
        # Press Windows key + S to open search
        pyautogui.hotkey('win', 's')
        time_module.sleep(1)  # Wait for search box to open
        
        # Type the app name
        pyautogui.typewrite(app, interval=0.05)
        time_module.sleep(1)  # Wait for search results to populate
        
        # Press Enter to open the first result
        pyautogui.press('enter')
        time_module.sleep(2)  # Wait for app to start
        
        speak(f"Opening {app}")
        log_interaction(command, f"Opening {app} via Windows Search", source="windows_search")
        
        # If there's remaining text, process it
        if remaining_text and remaining_text.strip():
            _process_remaining_text(remaining_text)
        
        return True
    except ImportError:
        speak("Error: pyautogui is not installed. Installing it...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyautogui"], 
                         capture_output=True, check=True)
            # Try again after installation
            return _open_app_with_windows_search(app, command, remaining_text)
        except Exception as e:
            print(f"Could not install pyautogui: {e}")
            speak("Could not open the app. Please check if it's installed.")
            return False
    except Exception as e:
        print(f"Error opening app with Windows Search: {e}")
        speak("Could not open the app. Please try again.")
        return False


def _open_app_legacy(app, app_clean, command, remaining_text):
    """Legacy method for opening apps (non-Windows or fallback)"""
    try:
        # Try to find the app from installed apps
        installed_apps = find_installed_apps()
        
        # Search for the app (exact match first, then partial match)
        matched_app = None
        if app_clean in installed_apps:
            matched_app = app_clean
        else:
            # Partial match search
            for app_key in installed_apps:
                if app_clean in app_key or app_key in app_clean:
                    matched_app = app_key
                    break
        
        if matched_app:
            try:
                if OS == "windows":
                    subprocess.run(["cmd", "/c", "start", matched_app], shell=True)
                elif OS == "darwin":
                    subprocess.run(["open", "-a", matched_app], capture_output=True)
                elif OS == "linux":
                    subprocess.run([matched_app], capture_output=True)
                
                speak(f"Opening {app}")
                log_interaction(command, f"Opening {app}", source="local")
                
                # If there's remaining text, process it
                if remaining_text and remaining_text.strip():
                    _process_remaining_text(remaining_text)
                return True
            except Exception as e:
                print(f"Error launching app: {e}")
        
        # If not found in registry, try direct launch
        try:
            if OS == "windows":
                subprocess.run(["cmd", "/c", "start", app_clean], shell=True)
            elif OS == "darwin":
                subprocess.run(["open", "-a", app_clean], capture_output=True)
            elif OS == "linux":
                subprocess.run(["xdg-open", app_clean], capture_output=True)
            
            speak(f"Opening {app}")
            log_interaction(command, f"Opening {app}", source="local")
            
            # If there's remaining text, process it with Gemini
            if remaining_text and remaining_text.strip():
                _process_remaining_text(remaining_text)
            return True
        except Exception as e:
            speak("Sorry, I couldn't open that app.")
            return False
    except Exception as e:
        speak("Sorry, I couldn't open that app.")
        return False

def _process_remaining_text(text):
    """Helper function to process remaining text with Gemini
    
    BUT: Don't process if text is just app control commands (close, shutdown, etc)
    or common app-related keywords that shouldn't trigger Gemini
    """
    import gemini_client
    
    # Keywords that shouldn't trigger Gemini processing
    skip_keywords = [
        'app', 'application', 'software', 'program',
        'tool', 'utility', 'system', 'desktop',
        'open', 'launch', 'start', 'run'
    ]
    
    text_lower = text.lower().strip()
    
    # Check if text is just a single skip keyword or close command
    if text_lower in skip_keywords or re.search(r'\b(close|shut|kill|terminate|stop|shutdown)\b', text, re.IGNORECASE):
        # This is just a control keyword or command, don't process through Gemini
        return False
    
    time.sleep(1)  # Give the app time to launch
    speak(f"Now, {text}")
    stream_flag = os.getenv("GEMINI_API_STREAM", "").lower() in ("1", "true", "yes")
    
    if stream_flag:
        try:
            gen = gemini_client.stream_generate(text)
            final_text = speak_stream(gen)
            
            if not final_text:
                return True
            
            cleaned = gemini_client.normalize_response(final_text)
            final_clean = gemini_client.strip_json_noise(cleaned)
            
            if final_clean:
                print(final_clean)
                speak(final_clean)
                log_interaction(text, final_clean, source="gemini_stream")
                
        except Exception as e:
            print(f"Streaming error: {e}")
            speak("Sorry, there was an error with the response.")
    else:
        response = gemini_client.generate_response(text)
        if response:
            cleaned = gemini_client.normalize_response(response)
            final_clean = gemini_client.strip_json_noise(cleaned)
            
            if final_clean:
                print(final_clean)
                speak(final_clean)
            else:
                print(response)
                speak(response)
            log_interaction(text, final_clean if final_clean else response, source="gemini")
        else:
            speak("Sorry, I couldn't generate a response.")
    
    return True


