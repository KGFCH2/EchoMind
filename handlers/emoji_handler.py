"""Emoji mode handler - opens emoji selector using F1 key"""
import re
import subprocess
import time
from config.settings import OS
from utils.voice_io import speak
from utils.logger import log_interaction

# Try different keyboard control methods
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from pynput.keyboard import Controller, Key
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

# Try keyboard module for raw key simulation
try:
    import keyboard
    KEYBOARD_MODULE_AVAILABLE = True
except ImportError:
    KEYBOARD_MODULE_AVAILABLE = False


def open_emoji_windows():
    """Open emoji panel on Windows using Win+. (Windows key + period)"""
    return open_emoji_windows_win_period()


def open_emoji_windows_low_level():
    """Low-level Windows key press using ctypes to send a real F1 press.

    This uses keybd_event (Win32) as a last-resort when higher-level libraries
    (keyboard/pyautogui/pynput) don't trigger the device's F1 mapping.
    """
    try:
        import ctypes
        from ctypes import wintypes

        # Virtual-key code for F1
        VK_F1 = 0x70
        # keybd_event is simpler and widely-supported; will synthesize a real key event
        user32 = ctypes.WinDLL('user32', use_last_error=True)

        # Press
        user32.keybd_event(VK_F1, 0, 0, 0)
        time.sleep(0.05)
        # Release
        user32.keybd_event(VK_F1, 0, 2, 0)
        time.sleep(0.3)
        return True
    except Exception as e:
        print(f"Low-level F1 send failed: {e}")
        return False


def open_emoji_windows_win_period():
    """Send Windows key + . (period) to open the emoji panel on Windows.

    This synthesizes a left-Windows-key down, period press, then releases both.
    Uses ctypes `keybd_event` which is widely supported on Windows.
    """
    try:
        import ctypes
        # Virtual-Key codes
        VK_LWIN = 0x5B
        VK_OEM_PERIOD = 0xBE  # OEM period/greater-than on US keyboards

        user32 = ctypes.WinDLL('user32', use_last_error=True)

        # Press Left Windows
        user32.keybd_event(VK_LWIN, 0, 0, 0)
        time.sleep(0.02)
        # Press period
        user32.keybd_event(VK_OEM_PERIOD, 0, 0, 0)
        time.sleep(0.02)
        # Release period
        user32.keybd_event(VK_OEM_PERIOD, 0, 2, 0)
        time.sleep(0.02)
        # Release Left Windows
        user32.keybd_event(VK_LWIN, 0, 2, 0)
        time.sleep(0.25)
        return True
    except Exception as e:
        print(f"Win+. send failed: {e}")
        return False


def open_emoji_linux():
    """Open emoji selector on Linux using Win+. (if available)"""
    return open_emoji_windows_win_period()


def open_emoji_mac():
    """Open emoji picker on macOS using Win+. (if available, or fallback)"""
    return open_emoji_windows_win_period()


def open_emoji():
    """Open emoji selector on any OS"""
    if OS == "windows":
        return open_emoji_windows()
    elif OS == "darwin":
        return open_emoji_mac()
    elif OS == "linux":
        return open_emoji_linux()
    else:
        return False


def handle_emoji_mode(command):
    """Handle emoji mode/picker commands
    
    Supports:
    - "Open emoji" / "Show emoji" / "emoji" -> Opens emoji picker (Win+.)
    - "Give me some emoji" / "Suggest emojis" / "emoji suggestions" -> Uses Gemini to suggest emojis
    """
    # Check if command contains "emoji" keyword
    if "emoji" not in command.lower():
        return False
    
    command_lower = command.lower()
    
    # Check if user is asking for emoji suggestions/recommendations (not just opening picker)
    if re.search(r'\b(suggest|give me|recommend|show me|some|list|examples?|types?)\b', command_lower):
        # User wants emoji suggestions - let Gemini handle this
        # Return False so it falls through to Gemini
        return False
    
    # Otherwise, open the emoji picker directly with Win+.
    success = open_emoji()
    
    if success:
        speak("Opening emoji picker")
        log_interaction(command, "Emoji picker opened (Win+.)", source="local")
    else:
        speak("Tried to open emoji picker but it may not be supported on this system.")
        log_interaction(command, "Emoji picker requested", source="local")
    return True


if __name__ == "__main__":
    print("Emoji handler test - import successful")
    print(f"OS detected: {OS}")
    print("Handler functions available:")
    print("- handle_emoji_mode(command)")
    print("- open_emoji_windows()")
    print("- open_emoji_mac()")
    print("- open_emoji_linux()")
