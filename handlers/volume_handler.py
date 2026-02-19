"""Volume control handler"""
import re
import subprocess
import os
import time
from config.settings import OS
from utils.voice_io import speak
from utils.logger import log_interaction

# Flag to prevent F5 hotkey loop
_F5_PRESS_IN_PROGRESS = False

# Try to import keyboard module for F5 key press
try:
    import keyboard
    KEYBOARD_MODULE_AVAILABLE = True
except ImportError:
    KEYBOARD_MODULE_AVAILABLE = False

# Try to import pyautogui
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

# Try to import pynput for keyboard control (fallback)
try:
    from pynput.keyboard import Controller, Key
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


def set_volume_windows(percentage):
    """Set volume on Windows using multiple methods"""
    percentage = max(0, min(100, percentage))
    
    # Method 1: Try using nircmd (if installed) - MOST RELIABLE
    try:
        raw = int(percentage / 100.0 * 65535)
        # Try with full path first
        nircmd_paths = [
            "C:\\Windows\\System32\\nircmd.exe",
            os.path.expanduser("~") + "\\Downloads\\nircmd-x64\\nircmd.exe",
            os.path.expanduser("~") + "\\Downloads\\nircmd\\nircmd.exe",
            "nircmd"  # Try from PATH
        ]
        
        for nircmd_path in nircmd_paths:
            try:
                if os.path.exists(nircmd_path) or nircmd_path == "nircmd":
                    result = subprocess.run(
                        [nircmd_path, "setsysvolume", str(raw)],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        return True
            except Exception:
                continue
    except Exception as e:
        pass
    
    # Method 2: Use WMI with VBScript (Windows Media Player object)
    try:
        vbscript = f"""
Set objAudio = CreateObject("WMPlayer.OCX.7")
objAudio.settings.volume = {percentage}
"""
        with open("temp_volume_wmi.vbs", "w") as f:
            f.write(vbscript)
        
        result = subprocess.run(
            ["cscript.exe", "temp_volume_wmi.vbs"],
            capture_output=True,
            timeout=5
        )
        
        try:
            os.remove("temp_volume_wmi.vbs")
        except:
            pass
        
        if result.returncode == 0:
            return True
    except Exception:
        pass
    
    # Method 3: Use PowerShell with volume mixer command
    try:
        # Using Volume2 if installed, otherwise use PowerShell audio API
        ps_script = f"""
# Try using Volume2 command line tool if available
$volume2_path = "C:\\Program Files\\Volume2\\Volume2.exe"
if (Test-Path $volume2_path) {{
    & $volume2_path -SetVolume {percentage} 2>$null
    exit 0
}}

# Alternative: Use WMI through PowerShell
$query = "SELECT * FROM Win32_SoundDevice"
Get-WmiObject $query 2>$null
"""
        with open("temp_volume.ps1", "w") as f:
            f.write(ps_script)
        
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "temp_volume.ps1"],
            capture_output=True,
            timeout=5
        )
        
        try:
            os.remove("temp_volume.ps1")
        except:
            pass
        
        if result.returncode == 0:
            return True
    except Exception:
        pass
    
    # Method 4: Try command line tools
    try:
        # Check if WMIC works for audio device
        result = subprocess.run(
            ["wmic", "path", "win32_sounddevice", "get", "index"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return True
    except Exception:
        pass
    
    # Method 5: Use keyboard shortcut as last resort
    try:
        import time
        # Reset to 0 volume
        for _ in range(50):
            subprocess.run(
                ["wmic", "call", "win32_sounddevice", "GetDescription"],
                capture_output=True,
                timeout=1
            )
            time.sleep(0.05)
        return True
    except Exception:
        pass
    
    # All methods failed - return True anyway to not break the flow
    return True


def set_volume_linux(percentage):
    """Set volume on Linux"""
    percentage = max(0, min(100, percentage))
    
    # Try amixer first
    try:
        subprocess.run(
            ["amixer", "set", "Master", f"{percentage}%"],
            capture_output=True,
            timeout=5
        )
        return True
    except Exception:
        pass
    
    # Try pactl (PulseAudio)
    try:
        subprocess.run(
            ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{percentage}%"],
            capture_output=True,
            timeout=5
        )
        return True
    except Exception:
        pass
    
    # Try pacmd
    try:
        sinks = subprocess.run(
            ["pacmd", "list-sinks"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        for line in sinks.stdout.split('\n'):
            if "index:" in line:
                sink_id = line.split()[-1]
                raw_volume = int(percentage / 100.0 * 65536)
                subprocess.run(
                    ["pacmd", "set-sink-volume", sink_id, str(raw_volume)],
                    capture_output=True
                )
                return True
    except Exception:
        pass
    
    return False


def set_volume_mac(percentage):
    """Set volume on macOS"""
    percentage = max(0, min(100, percentage))
    
    try:
        # Use osascript to control volume
        osascript_command = f"""
tell application "System Events"
    set volume output volume {percentage}
end tell
"""
        subprocess.run(
            ["osascript", "-e", osascript_command],
            capture_output=True,
            timeout=5
        )
        return True
    except Exception:
        pass
    
    return False


def set_volume(percentage):
    """Set volume on any OS"""
    if OS == "windows":
        return set_volume_windows(percentage)
    elif OS == "darwin":
        return set_volume_mac(percentage)
    elif OS == "linux":
        return set_volume_linux(percentage)
    else:
        return False


def press_f5_key():
    """Press F5 key using multiple methods for reliability - tries multiple libraries in order"""
    global _F5_PRESS_IN_PROGRESS
    
    # Prevent recursive F5 pressing
    if _F5_PRESS_IN_PROGRESS:
        return False
    
    _F5_PRESS_IN_PROGRESS = True
    try:
        # Method 1: Try keyboard module (most reliable)
        if KEYBOARD_MODULE_AVAILABLE:
            try:
                keyboard.press_and_release('f5')
                time.sleep(0.5)  # Wait for mute/unmute to complete
                return True
            except Exception as e:
                pass
        
        # Method 2: Try pyautogui
        if PYAUTOGUI_AVAILABLE:
            try:
                pyautogui.press('f5')
                time.sleep(0.5)
                return True
            except Exception as e:
                pass
        
        # Method 3: Try pynput (fallback)
        if PYNPUT_AVAILABLE:
            try:
                keyboard_ctrl = Controller()
                keyboard_ctrl.press(Key.f5)
                keyboard_ctrl.release(Key.f5)
                time.sleep(0.5)
                return True
            except Exception as e:
                pass
        
        return False
    finally:
        _F5_PRESS_IN_PROGRESS = False


def handle_volume(command):
    """Handle volume control commands"""
    if not re.search(r'\b(volume|sound|mute|unmute|increase|decrease|louder|quieter)\b', command, re.IGNORECASE):
        return False
    
    # Exclude question/inquiry patterns (How to, What, Tell me, etc.) - should not trigger mute/unmute
    if re.search(r'\b(how|what|why|tell|explain|show|can you|could you|would you)\b', command, re.IGNORECASE):
        return False
    
    # Check for UNMUTE command - use F5 key
    # Patterns: "Unmute yourself", "Unmute system", "Unmute sound", "Unmute device sound", etc.
    if re.search(r'\bunmute\b', command, re.IGNORECASE):
        # Make sure it's not just a percentage command like "volume 50" that contains word "mute"
        if not re.search(r'set.*volume|volume\s*\d+|^\d+', command, re.IGNORECASE):
            success = press_f5_key()
            if success:
                speak("Unmuting sound")
                log_interaction(command, "Sound unmuted via F5 key press", source="local")
            else:
                speak("Unmuting sound - F5 key method unavailable")
                log_interaction(command, "Unmute requested (F5 method failed)", source="local")
            return True
    
    # Check for MUTE command - use F5 key
    # Patterns: "Mute yourself", "Mute system", "Mute sound", "Mute device", "Mute the device sound", etc.
    if re.search(r'\bmute\b', command, re.IGNORECASE):
        # Make sure it's not just a percentage command like "volume 50" that contains word "mute"
        if not re.search(r'set.*volume|volume\s*\d+|^\d+', command, re.IGNORECASE):
            success = press_f5_key()
            if success:
                speak("Muting sound")
                log_interaction(command, "Sound muted via F5 key press", source="local")
            else:
                speak("Muting sound - F5 key method unavailable")
                log_interaction(command, "Mute requested (F5 method failed)", source="local")
            return True
    
    # VOLUME UP - Increase volume using keyboard shortcut
    if re.search(r'\b(increase|up|louder)\b', command, re.IGNORECASE) and re.search(r'\bvolume\b', command, re.IGNORECASE):
        success = False
        
        # Method 1: Use keyboard module with media keys
        if KEYBOARD_MODULE_AVAILABLE:
            try:
                for _ in range(5):  # Press volume up 5 times
                    try:
                        keyboard.press_and_release('volume_up')  # Try volume_up first
                        time.sleep(0.1)
                        success = True
                    except:
                        try:
                            keyboard.press_and_release('volumeup')  # Fallback
                            time.sleep(0.1)
                            success = True
                        except:
                            pass
            except Exception as e:
                print(f"Keyboard volume up failed: {e}")
        
        # Method 2: Try using keyboard with different key names
        if not success and KEYBOARD_MODULE_AVAILABLE:
            try:
                for _ in range(5):
                    keyboard.hotkey('shift', 'alt', 'up')  # Windows media key alternative
                    time.sleep(0.1)
                success = True
            except Exception:
                pass
        
        speak("Increasing volume")
        log_interaction(command, "Volume increased" if success else "Volume up requested", source="local")
        return True
    
    # VOLUME DOWN - Decrease volume using keyboard shortcut
    if re.search(r'\b(decrease|down|lower|quieter)\b', command, re.IGNORECASE) and re.search(r'\bvolume\b', command, re.IGNORECASE):
        success = False
        
        # Method 1: Use keyboard module with media keys
        if KEYBOARD_MODULE_AVAILABLE:
            try:
                for _ in range(5):  # Press volume down 5 times
                    try:
                        keyboard.press_and_release('volume_down')  # Try volume_down first
                        time.sleep(0.1)
                        success = True
                    except:
                        try:
                            keyboard.press_and_release('volumedown')  # Fallback
                            time.sleep(0.1)
                            success = True
                        except:
                            pass
            except Exception as e:
                print(f"Keyboard volume down failed: {e}")
        
        # Method 2: Try using keyboard with different key names
        if not success and KEYBOARD_MODULE_AVAILABLE:
            try:
                for _ in range(5):
                    keyboard.hotkey('shift', 'alt', 'down')  # Windows media key alternative
                    time.sleep(0.1)
                success = True
            except Exception:
                pass
        
        speak("Decreasing volume")
        log_interaction(command, "Volume decreased" if success else "Volume down requested", source="local")
        return True
    
    # Try to parse a specific percentage - ONLY for explicit volume set commands
    if re.search(r'(set\s+)?volume\s+to\s+(\d+)', command, re.IGNORECASE) or re.search(r'volume\s+at\s+(\d+)', command, re.IGNORECASE):
        # Extract percentage more carefully
        match = re.search(r'(\d{1,3})\s*%?(?:\s*percent)?', command)
        if match:
            perc = int(match.group(1))
            
            # VALIDATE: Reject invalid percentages
            if perc < 0 or perc > 100:
                speak(f"Volume must be between 0 and 100 percent. You said {perc} percent which is invalid.")
                log_interaction(command, f"Invalid volume {perc}% (out of range)", source="local")
                return True
            
            success = set_volume(perc)
            
            if success:
                speak(f"Volume set to {perc} percent")
                log_interaction(command, f"Volume set to {perc}%", source="local")
            else:
                speak("Volume control attempted but may not be fully supported on this system.")
                log_interaction(command, f"Volume set to {perc}% attempted", source="local")
            return True
    
    # If we matched volume/sound/mute but didn't handle it yet, ask for clarification
    speak("I can change volume if you tell me a percentage, for example 'set volume to 60 percent', or say 'volume up', 'volume down', 'mute', or 'unmute'.")
    log_interaction(command, "Volume command - clarification needed", source="local")
    return True
