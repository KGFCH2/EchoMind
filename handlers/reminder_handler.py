"""Reminder handler - Set and monitor reminders/tasks"""
import re
import threading
import time
import datetime
from utils.voice_io import speak
from utils.logger import log_interaction

# List to store active reminders: {"hour": HH, "minute": MM, "period": "AM/PM", "label": "task", "triggered": False}
ACTIVE_REMINDERS = []
REMINDER_THREAD_STARTED = False

def handle_reminder(command):
    """
    Handle reminder commands.
    Supports: Set ("remind me to...", "set a reminder for..."), Remove, and List.
    """
    global ACTIVE_REMINDERS
    command_lower = command.lower()
    
    # Filter: Listen for keywords related to reminders or timers
    if not any(word in command_lower for word in ["remind", "reminder", "alarm", "wake me up"]):
        return False

    # 1. HANDLE LISTING REMINDERS
    if any(word in command_lower for word in ["list", "show", "what", "check"]):
        active = [r for r in ACTIVE_REMINDERS if not r["triggered"]]
        if not active:
            speak("You have no active reminders.")
        else:
            speak(f"You have {len(active)} active reminders.")
            for r in active:
                display = f"{r['hour']}:{r['minute']:02d} {r['period'] if r['period'] else ''}".strip()
                speak(f"One at {display}")
        return True

    # 2. HANDLE REMOVING REMINDERS
    if any(word in command_lower for word in ["remove", "cancel", "delete", "clear", "stop"]):
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', command_lower)
        if time_match:
            h = int(time_match.group(1))
            m = int(time_match.group(2)) if time_match.group(2) else 0
            p = time_match.group(3).upper() if time_match.group(3) else None
            
            initial_count = len(ACTIVE_REMINDERS)
            # Remove matching reminder
            ACTIVE_REMINDERS = [r for r in ACTIVE_REMINDERS if not (r['hour'] == h and r['minute'] == m and r['period'] == p)]
            
            if len(ACTIVE_REMINDERS) < initial_count:
                display = f"{h}:{m:02d} {p if p else ''}".strip()
                speak(f"Removed reminder for {display}")
                log_interaction(command, f"Removed reminder {display}", source="local")
            else:
                speak("I couldn't find a reminder for that exact time.")
            return True
        else:
            if ACTIVE_REMINDERS:
                speak("Which reminder should I remove? Please specify the time.")
            else:
                speak("You don't have any reminders to remove.")
            return True

    # 3. HANDLE SETTING REMINDERS
    # Broadened matching to catch "9:48 PM" directly or "remind me at 9:48"
    time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', command_lower)

    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        period = time_match.group(3).upper() if time_match.group(3) else None
        
        # Validation for 12h vs 24h
        if hour > 12 and period:
            period = None # PM/AM not valid for 24h format
        if hour > 23 or minute > 59:
            speak("That's an invalid time. Please try again.")
            return True

        display = f"{hour}:{minute:02d} {period if period else ''}".strip()
        
        # Avoid duplicate identical reminders
        if any(r for r in ACTIVE_REMINDERS if r['hour'] == hour and r['minute'] == minute and r['period'] == period and not r['triggered']):
             speak(f"You already have a reminder set for {display}.")
             return True

        ACTIVE_REMINDERS.append({
            "hour": hour,
            "minute": minute,
            "period": period,
            "triggered": False
        })
        
        speak(f"Ok, I will remind you at {display}.")
        log_interaction(command, f"Reminder set for {display}", source="local")
        
        _start_reminder_monitor()
        return True
    
    return False

def _start_reminder_monitor():
    """Start the background thread to check reminders"""
    global REMINDER_THREAD_STARTED
    if not REMINDER_THREAD_STARTED:
        monitor_thread = threading.Thread(target=_monitor_reminders, daemon=True)
        monitor_thread.start()
        REMINDER_THREAD_STARTED = True

def _monitor_reminders():
    """Background loop to check if a reminder should trigger"""
    while True:
        try:
            now = datetime.datetime.now()
            current_hour_24 = now.hour
            current_minute = now.minute
            
            # Using a copy to avoid modification during iteration
            for reminder in list(ACTIVE_REMINDERS):
                if reminder["triggered"]:
                    continue
                
                target_hour = int(reminder["hour"])
                target_minute = int(reminder["minute"])
                period = reminder["period"]
                
                # Convert to 24h for comparison
                orig_target_hour = target_hour
                if period == "PM" and target_hour < 12:
                    target_hour += 12
                elif period == "AM" and target_hour == 12:
                    target_hour = 0
                
                if current_hour_24 == target_hour and current_minute == target_minute:
                    # TRIGGER REMINDER
                    reminder_display = f"{orig_target_hour}:{target_minute:02d} {period if period else ''}".strip()
                    speak(f"BEEP BEEP! This is your reminder for {reminder_display}!")
                    reminder["triggered"] = True
                    # Clean up the list
                    if reminder in ACTIVE_REMINDERS:
                        ACTIVE_REMINDERS.remove(reminder)
            
            # Check every 20 seconds for better responsiveness
            time.sleep(20)
        except Exception as e:
            time.sleep(5)
