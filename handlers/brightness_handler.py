"""Brightness control handler for Windows systems"""
import re
import subprocess
import os
from config.settings import OS
from utils.voice_io import speak
from utils.logger import log_interaction


# Dictionary to convert written numbers to integers
NUMBER_WORDS = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
    'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20,
    'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
    'eighty': 80, 'ninety': 90, 'hundred': 100
}


def parse_brightness_value(command):
    """Parse brightness percentage from command text
    
    Supports:
    - "Make brightness 40%"
    - "Make brightness 40"
    - "Make brightness seventy"
    - "Set brightness to fifty"
    """
    # Try to find a percentage first (e.g., "40%")
    match = re.search(r'(\d{1,3})\s*%', command, re.IGNORECASE)
    if match:
        value = int(match.group(1))
        return value if 0 <= value <= 100 else None
    
    # Try to find a number without percent (e.g., "40")
    match = re.search(r'\b(\d{1,3})\b', command)
    if match:
        value = int(match.group(1))
        return value if 0 <= value <= 100 else None
    
    # Try to find written numbers (e.g., "seventy")
    for word, value in NUMBER_WORDS.items():
        if re.search(rf'\b{word}\b', command, re.IGNORECASE):
            return value if 0 <= value <= 100 else None
    
    return None


def set_brightness_windows(percentage):
    """Set brightness on Windows using multiple methods"""
    percentage = max(0, min(100, percentage))
    
    # Method 1: Try using nircmd with F2/F3 simulation
    try:
        # Calculate how many times to press F3 (increase) or F2 (decrease)
        # Assuming F3 increases brightness and F2 decreases it
        # We'll try to set it by pressing keys multiple times
        
        # First, try nircmd
        nircmd_paths = [
            "C:\\Windows\\System32\\nircmd.exe",
            os.path.expanduser("~") + "\\Downloads\\nircmd-x64\\nircmd.exe",
            os.path.expanduser("~") + "\\Downloads\\nircmd\\nircmd.exe",
            "nircmd"
        ]
        
        for nircmd_path in nircmd_paths:
            try:
                if os.path.exists(nircmd_path) or nircmd_path == "nircmd":
                    # Use nircmd to set brightness via WMI
                    result = subprocess.run(
                        [nircmd_path, "setbrightness", str(percentage)],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        return True
            except Exception:
                continue
    except Exception:
        pass
    
    # Method 2: Use PowerShell WMI to set brightness
    try:
        ps_script = f"""
$brightness = {percentage}
$wmi = Get-WmiObject -Namespace root\\wmi -Class WmiMonitorBrightnessMethods
if ($wmi -ne $null) {{
    $wmi.WmiSetBrightness(1, $brightness) | Out-Null
    exit 0
}} else {{
    exit 1
}}
"""
        with open("temp_brightness.ps1", "w") as f:
            f.write(ps_script)
        
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "temp_brightness.ps1"],
            capture_output=True,
            timeout=5
        )
        
        try:
            os.remove("temp_brightness.ps1")
        except:
            pass
        
        if result.returncode == 0:
            return True
    except Exception:
        pass
    
    # Method 3: Use keyboard simulation with F2/F3 keys
    # This is the fallback method that simulates keypresses
    try:
        import pynput.keyboard
        from pynput.keyboard import Controller, Key
        from time import sleep
        
        keyboard = Controller()
        
        # Determine if we need to increase or decrease
        # We'll assume current brightness is 50% and adjust from there
        target_presses = int(percentage / 5)  # Each key press changes 5%
        
        # Try to adjust brightness using F2 (decrease) and F3 (increase)
        if percentage < 50:
            # Use F2 to decrease
            presses_needed = int((50 - percentage) / 5)
            for _ in range(presses_needed):
                keyboard.press(Key.f2)
                keyboard.release(Key.f2)
                sleep(0.2)
        elif percentage > 50:
            # Use F3 to increase
            presses_needed = int((percentage - 50) / 5)
            for _ in range(presses_needed):
                keyboard.press(Key.f3)
                keyboard.release(Key.f3)
                sleep(0.2)
        
        return True
    except Exception:
        pass
    
    # Method 4: Try using monitorian command line tool
    try:
        result = subprocess.run(
            ["monitorian", "-set", str(percentage)],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            return True
    except Exception:
        pass
    
    return False


def set_brightness_linux(percentage):
    """Set brightness on Linux"""
    percentage = max(0, min(100, percentage))
    
    # Try xrandr
    try:
        # Convert percentage to brightness value (0.0 - 1.0)
        brightness_value = percentage / 100.0
        result = subprocess.run(
            ["xrandr", "--output", "HDMI-1", "--brightness", str(brightness_value)],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            return True
    except Exception:
        pass
    
    # Try acpi_video backlight
    try:
        max_brightness = 100
        current = int(percentage * max_brightness / 100)
        with open("/sys/class/backlight/acpi_video0/brightness", "w") as f:
            f.write(str(current))
        return True
    except Exception:
        pass
    
    return False


def set_brightness_mac(percentage):
    """Set brightness on macOS"""
    percentage = max(0, min(100, percentage))
    
    try:
        # Use osascript to control brightness
        osascript_command = f"""
tell application "System Events"
    key code 113 using function down  // F2 (or adjust to F3 for increase)
end tell
"""
        # Alternative using brightness tool
        subprocess.run(
            ["brightness", str(int(percentage / 100.0 * 16))],
            capture_output=True,
            timeout=5
        )
        return True
    except Exception:
        pass
    
    return False


def set_brightness(percentage):
    """Set brightness on any OS"""
    if OS == "windows":
        return set_brightness_windows(percentage)
    elif OS == "darwin":
        return set_brightness_mac(percentage)
    elif OS == "linux":
        return set_brightness_linux(percentage)
    else:
        return False


def handle_brightness(command):
    """Handle brightness control commands
    
    Supports:
    - "Make brightness 40%"
    - "Make brightness 40"
    - "Make brightness seventy"
    - "Set brightness to fifty"
    - "Brightness 80"
    """
    if not re.search(r'\b(brightness|screen brightness|display brightness)\b', command, re.IGNORECASE):
        return False
    
    # Parse the brightness value from the command
    brightness_value = parse_brightness_value(command)
    
    if brightness_value is not None:
        # Validate percentage
        if brightness_value < 0 or brightness_value > 100:
            speak(f"Brightness must be between 0 and 100 percent. You said {brightness_value} percent which is invalid.")
            log_interaction(command, f"Invalid brightness {brightness_value}% (out of range)", source="local")
            return True
        
        # Try to set brightness
        success = set_brightness(brightness_value)
        
        if success:
            speak(f"Set brightness to {brightness_value} percent")
            log_interaction(command, f"Set brightness to {brightness_value}%", source="local")
        else:
            speak(f"Brightness control attempted to set {brightness_value} percent but may not be fully supported on this system.")
            log_interaction(command, f"Brightness change requested to {brightness_value}%", source="local")
        return True
    else:
        # Try generic brightness commands
        if "increase" in command.lower() or "up" in command.lower():
            speak("Increasing the brightness")
            set_brightness(75)  # Set to 75% as default increase
            log_interaction(command, "Brightness increase requested", source="local")
        elif "decrease" in command.lower() or "down" in command.lower():
            speak("Decreasing the brightness")
            set_brightness(25)  # Set to 25% as default decrease
            log_interaction(command, "Brightness decrease requested", source="local")
        else:
            speak("I can change brightness if you tell me a percentage, for example 'set brightness to 60' or 'make brightness seventy'.")
        log_interaction(command, "Brightness command", source="local")
        return True
