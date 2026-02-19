"""Tab navigation handler - Navigate to specific tabs in browsers using Ctrl+number"""
import re
import time
from config.settings import OS
from utils.voice_io import speak
from utils.logger import log_interaction


# Current tab tracking
CURRENT_TAB = None  # Track which tab user is currently on


def set_current_tab(tab_number):
    """Track which tab the user is currently on"""
    global CURRENT_TAB
    CURRENT_TAB = tab_number


def get_current_tab():
    """Get the current tab number"""
    return CURRENT_TAB


def handle_tab_navigation(command):
    """Handle tab navigation commands using Ctrl+number
    
    Supports:
    - "move to 1st tab" → Presses Ctrl+1
    - "go to 3rd tab" → Presses Ctrl+3
    - "move 5th tab" → Presses Ctrl+5
    - "tab 9" → Presses Ctrl+9
    - "first tab" → Presses Ctrl+1
    - "last tab" → Presses Ctrl+9 (Chrome/Edge/Firefox support Ctrl+9 for last tab)
    - "next tab" → Presses Ctrl+Tab
    - "previous tab" → Presses Ctrl+Shift+Tab
    - "move to the 2nd tab" → Presses Ctrl+2
    
    Returns True if command was handled, False otherwise
    """
    command_lower = command.lower().strip()
    
    # Check if this is a tab navigation command
    if not re.search(r'\b(move|go|switch|navigate)\s+(to|to\s+the)?\s*(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|last|next|previous|\d+(?:st|nd|rd|th)?|tab)', command_lower):
        return False
    
    # Pattern 1: Numeric tab numbers - "move to 3rd tab" or "tab 5"
    numeric_match = re.search(r'(?:move|go|switch|navigate)?\s*(?:to)?\s*(?:the)?\s*(\d+)(?:st|nd|rd|th)?\s*tab', command_lower)
    if numeric_match:
        tab_num = int(numeric_match.group(1))
        if 1 <= tab_num <= 8:
            return _navigate_to_tab(tab_num, command)
        else:
            speak(f"Tab {tab_num} is out of range. Browsers support tabs 1 to 8 with Ctrl+number shortcut.")
            return True
    
    # Pattern 2: Word-based tab numbers - "move to first tab"
    word_tabs = {
        'first': 1, 'second': 2, 'third': 3, 'fourth': 4,
        'fifth': 5, 'sixth': 6, 'seventh': 7, 'eighth': 8,
        'ninth': 9
    }
    
    word_match = re.search(r'(?:move|go|switch|navigate)\s+(?:to)?\s*(?:the)?\s*(' + '|'.join(word_tabs.keys()) + r')\s+tab', command_lower)
    if word_match:
        tab_word = word_match.group(1)
        tab_num = word_tabs[tab_word]
        if tab_num <= 8:
            return _navigate_to_tab(tab_num, command)
        else:
            speak("Tab position out of supported range. Use tabs 1 to 8.")
            return True
    
    # Pattern 3: Next tab - "next tab"
    if re.search(r'\bnext\s+tab\b', command_lower):
        return _navigate_next_tab(command)
    
    # Pattern 4: Previous tab - "previous tab"
    if re.search(r'\bprevious\s+tab\b|\bprev\s+tab\b', command_lower):
        return _navigate_previous_tab(command)
    
    # Pattern 5: Last tab - "move to last tab"
    if re.search(r'(?:move|go|switch|navigate)\s+(?:to)?\s*(?:the)?\s+last\s+tab', command_lower):
        return _navigate_to_last_tab(command)
    
    # Pattern 6: Simple "tab X" format - "tab 3"
    simple_tab = re.search(r'^tab\s+(\d+)$', command_lower)
    if simple_tab:
        tab_num = int(simple_tab.group(1))
        if 1 <= tab_num <= 8:
            return _navigate_to_tab(tab_num, command)
        else:
            speak(f"Tab {tab_num} is out of range. Browsers support tabs 1 to 8 with Ctrl+number shortcut.")
            return True
    
    return False


def _navigate_to_tab(tab_number, command):
    """Navigate to a specific tab using Ctrl+number
    
    Works on:
    - Google Chrome
    - Microsoft Edge
    - Mozilla Firefox
    - Opera Browser
    - Brave Browser
    """
    try:
        import pyautogui
        
        # Send Ctrl+[tab_number] to switch to that tab
        pyautogui.hotkey('ctrl', str(tab_number))
        time.sleep(0.5)
        
        # Update tracking
        set_current_tab(tab_number)
        
        # Provide ordinal suffix
        ordinal_suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        suffix = ordinal_suffixes.get(tab_number, 'th')
        
        speak(f"Moving to {tab_number}{suffix} tab")
        log_interaction(command, f"Navigated to tab {tab_number}", source="local")
        return True
        
    except ImportError:
        # Try keyboard module as fallback
        try:
            import keyboard
            keyboard.press_and_release('ctrl+' + str(tab_number))
            time.sleep(0.5)
            set_current_tab(tab_number)
            
            ordinal_suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
            suffix = ordinal_suffixes.get(tab_number, 'th')
            
            speak(f"Moving to {tab_number}{suffix} tab")
            log_interaction(command, f"Navigated to tab {tab_number}", source="local")
            return True
        except:
            speak("Could not navigate to the tab. Please try manually.")
            return False
    except Exception as e:
        speak("Could not navigate to the tab. Please try manually.")
        print(f"Error navigating to tab: {e}")
        return False


def _navigate_next_tab(command):
    """Navigate to the next tab using Ctrl+Tab"""
    try:
        import pyautogui
        
        # Ctrl+Tab moves to the next tab
        pyautogui.hotkey('ctrl', 'tab')
        time.sleep(0.5)
        
        # Update current tab tracker (increment by 1, but we don't know absolute position)
        if CURRENT_TAB:
            set_current_tab(CURRENT_TAB + 1)
        
        speak("Moving to next tab")
        log_interaction(command, "Navigated to next tab using Ctrl+Tab", source="local")
        return True
        
    except ImportError:
        try:
            import keyboard
            keyboard.press_and_release('ctrl+tab')
            time.sleep(0.5)
            if CURRENT_TAB:
                set_current_tab(CURRENT_TAB + 1)
            speak("Moving to next tab")
            log_interaction(command, "Navigated to next tab", source="local")
            return True
        except:
            speak("Could not navigate to the next tab.")
            return False
    except Exception as e:
        speak("Could not navigate to the next tab.")
        print(f"Error navigating to next tab: {e}")
        return False


def _navigate_previous_tab(command):
    """Navigate to the previous tab using Ctrl+Shift+Tab"""
    try:
        import pyautogui
        
        # Ctrl+Shift+Tab moves to the previous tab
        pyautogui.hotkey('ctrl', 'shift', 'tab')
        time.sleep(0.5)
        
        # Update current tab tracker (decrement by 1)
        if CURRENT_TAB and CURRENT_TAB > 1:
            set_current_tab(CURRENT_TAB - 1)
        
        speak("Moving to previous tab")
        log_interaction(command, "Navigated to previous tab using Ctrl+Shift+Tab", source="local")
        return True
        
    except ImportError:
        try:
            import keyboard
            keyboard.press_and_release('ctrl+shift+tab')
            time.sleep(0.5)
            if CURRENT_TAB and CURRENT_TAB > 1:
                set_current_tab(CURRENT_TAB - 1)
            speak("Moving to previous tab")
            log_interaction(command, "Navigated to previous tab", source="local")
            return True
        except:
            speak("Could not navigate to the previous tab.")
            return False
    except Exception as e:
        speak("Could not navigate to the previous tab.")
        print(f"Error navigating to previous tab: {e}")
        return False


def _navigate_to_last_tab(command):
    """Navigate to the last tab using Ctrl+9
    
    Most browsers support Ctrl+9 to go to the last tab
    """
    try:
        import pyautogui
        
        # Ctrl+9 moves to the last tab in most browsers
        pyautogui.hotkey('ctrl', '9')
        time.sleep(0.5)
        
        speak("Moving to last tab")
        log_interaction(command, "Navigated to last tab using Ctrl+9", source="local")
        return True
        
    except ImportError:
        try:
            import keyboard
            keyboard.press_and_release('ctrl+9')
            time.sleep(0.5)
            speak("Moving to last tab")
            log_interaction(command, "Navigated to last tab", source="local")
            return True
        except:
            speak("Could not navigate to the last tab.")
            return False
    except Exception as e:
        speak("Could not navigate to the last tab.")
        print(f"Error navigating to last tab: {e}")
        return False
