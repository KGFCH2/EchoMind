"""Time and date utilities"""
import datetime
import pytz

def get_time():
    """Get current time in IST"""
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(ist)
    return now.strftime("%H:%M")

def get_date():
    """Get current date and day in IST"""
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(ist)
    date_str = now.strftime("%Y-%m-%d")
    day_str = now.strftime("%A")
    return f"{date_str}, and it's a {day_str}"

def get_greeting():
    """Get time-based greeting in IST"""
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(ist)
    hour = now.hour
    if 5 <= hour < 12:
        return "Good morning! I am EchoMind AI, your voice assistant. How can I help you?"
    elif 12 <= hour < 17:
        return "Good afternoon! I am EchoMind AI, your voice assistant. How can I help you?"
    elif 17 <= hour < 22:
        return "Good evening! I am EchoMind AI, your voice assistant. How can I help you?"
    else:
        return "Hey there! I am EchoMind AI, your voice assistant. It is time to rest after a hectic day."
