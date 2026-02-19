"""Resume file handler - opens resume directly"""
import re
import os
import subprocess
import webbrowser
from config.settings import OS
from utils.voice_io import speak
from utils.logger import log_interaction


def open_resume_windows(file_path):
    """Open resume file on Windows"""
    try:
        # Convert path to file:// URL format for safe opening
        if file_path.startswith("file://"):
            url = file_path
        else:
            # Convert Windows path to file URL
            url = file_path.replace("\\", "/")
            if not url.startswith("file://"):
                url = f"file:///{url}"
        
        # Use webbrowser to open PDF (works better than subprocess)
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"Resume opening error (Windows): {e}")
        try:
            # Fallback: Try direct file opening
            os.startfile(file_path)
            return True
        except Exception as e2:
            print(f"Resume fallback error: {e2}")
            return False


def open_resume_linux(file_path):
    """Open resume file on Linux"""
    try:
        # Try xdg-open first (standard on most Linux systems)
        subprocess.Popen(["xdg-open", file_path])
        return True
    except Exception:
        pass
    
    # Try other PDF viewers
    pdf_viewers = ["evince", "okular", "zathura", "mupdf"]
    for viewer in pdf_viewers:
        try:
            subprocess.Popen([viewer, file_path])
            return True
        except Exception:
            continue
    
    return False


def open_resume_mac(file_path):
    """Open resume file on macOS"""
    try:
        subprocess.Popen(["open", file_path])
        return True
    except Exception:
        return False


def open_resume(file_path):
    """Open resume file on any OS"""
    if OS == "windows":
        return open_resume_windows(file_path)
    elif OS == "darwin":
        return open_resume_mac(file_path)
    elif OS == "linux":
        return open_resume_linux(file_path)
    else:
        return False


def handle_resume_opening(command):
    """Handle resume opening commands
    
    Supports:
    - "Open my resume"
    - "Show resume"
    - "Open resume"
    - "Display my resume"
    - "Open my CV"
    - "Show my c v"
    - "Curriculum vitae"
    - Misspellings: "curriculam vitae", etc.
    """
    command_lower = command.lower()
    
    # Check if command contains resume-related keywords (with flexibility for spacing and misspellings)
    # Supports: resume, cv, c v, curriculum vitae, curricula, curriculam, etc.
    resume_pattern = r'\b(resume|c\.?v\.?|c\s+v|curricul[au]m\s+vitae|cv\.?)\b'
    if not re.search(resume_pattern, command_lower):
        return False
    
    # Check if it's a request to open
    if not re.search(r'\b(open|show|display|view|launch|start)\b', command_lower):
        return False
    
    # Resume file path - customize this to your actual resume location
    resume_path = "file:///E:/Personal%20Informations/Babin_Bid_Resume.pdf"
    
    try:
        success = open_resume(resume_path)
        
        if success:
            speak("Opening your resume")
            log_interaction(command, f"Resume opened: {resume_path}", source="local")
            return True
        else:
            speak("Tried to open your resume but encountered an issue.")
            log_interaction(command, "Resume opening attempted but failed", source="local")
            return True
    except Exception as e:
        print(f"Resume handler error: {e}")
        speak("Sorry, I couldn't open your resume.")
        log_interaction(command, f"Resume error: {e}", source="local")
        return True
