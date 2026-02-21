"""File writing handler for Notepad, Word, etc."""
import re
import subprocess
import time
import os
import pyautogui
from config.settings import OS
from utils.voice_io import speak, listen
from utils.logger import log_interaction
from clients import gemini_client


def handle_file_writing(command):
    """Handle writing content to files (Notepad, Word, etc.)
    
    Supports:
    - New: "Open notepad and write a story"
    - Append: "In the current notebook write a bengali song"
    """
    # Detect intent: Must mention a document app AND a writing action
    doc_apps = r'\b(notepad|notebook|word|document|ms\s+word|wordpad)\b'
    write_actions = r'\b(write|add|type|create|generate|put)\b'
    
    if not re.search(doc_apps, command, re.IGNORECASE) or not re.search(write_actions, command, re.IGNORECASE):
        return False
    
    command_lower = command.lower()
    
    # Determine if we need to open a new app or use the active one
    is_open_request = bool(re.search(r'\b(open|launch|start|new)\b', command_lower))
    is_append = "current" in command_lower or "active" in command_lower or "open" in command_lower or not is_open_request
    
    # Determine which app to open (if needed)
    app_name = "notepad" if "word" not in command_lower else "word"
    
    # Extract the writing prompt
    write_prompt = "a creative story"
    write_match = re.search(r'(?:write|add|type|create|generate|put)\s+(?:a\s+)?(.*?)(?:\s+(?:in|to|on)\s+.*)?$', command_lower)
    if write_match:
        extracted = write_match.group(1).strip()
        if len(extracted) > 2:
            write_prompt = extracted
    
    try:
        if is_open_request:
            # Open the application
            if OS == "windows":
                if app_name == "notepad":
                    subprocess.Popen(["notepad.exe"])
                elif app_name == "word":
                    subprocess.Popen(["winword.exe"])
            elif OS == "darwin":
                subprocess.Popen(["open", "-a", "TextEdit" if app_name == "notepad" else "Microsoft Word"])
            elif OS == "linux":
                subprocess.Popen(["gedit" if app_name == "notepad" else "libreoffice --writer"])
            
            speak(f"Opening {app_name}")
            # Wait for application to open
            time.sleep(3)
        else:
            speak(f"Continuing in your active {app_name}")
        
        # Generate content using Gemini
        speak(f"Generating {write_prompt}...")
        log_interaction(command, f"Writing {write_prompt} to {app_name} (append={is_append})", source="local")
        
        content = _generate_content(write_prompt)
        
        if content:
            # If appending to existing text, add the 5-line gap as requested
            if is_append and not is_open_request:
                content = "\n\n\n\n\n" + content
                
            speak("Writing to the document...")
            _type_into_document(content)
            
            speak(f"Finished writing to {app_name}")
            
            # Proactive follow-up
            time.sleep(1)
            speak("I am listening to you.... please tell me what to do next")
            return True
        else:
            speak("Sorry, I couldn't generate the content.")
            return False
    
    except Exception as e:
        speak(f"Sorry, there was an error with {app_name}.")
        print(f"File writing error: {e}")
        return False


def _generate_content(prompt):
    """Generate content using Gemini API with special handling for song lyrics"""
    try:
        command_lower = prompt.lower()
        
        # Check if the user is asking for specific song lyrics
        is_lyric_request = any(k in command_lower for k in ["song", "lyrics", "bole chudiyan", "tune", "sing"])
        
        if is_lyric_request:
            # Research-focused prompt for accurate lyrics
            full_prompt = (
                f"You are a helpful assistant. The user wants the ACTUAL and COMPLETE lyrics for the song: '{prompt}'. "
                "Please research your knowledge base for the precise lyrics of this song. "
                "Provide ONLY the lyrics text itself. Avoid generic generated songs. "
                "If it's a movie song (like from Kabhi Khushi Kabhie Gham), ensure the lyrics are accurate to that film."
            )
        elif not any(keyword in command_lower for keyword in ['story', 'poem', 'essay', 'article', 'tale', 'paragraph']):
            full_prompt = f"Write a short {prompt}. Keep it concise and interesting."
        else:
            full_prompt = prompt
        
        # Use blocking API for reliability
        response = gemini_client.generate_response(full_prompt)
        
        if response:
            # Clean the response
            cleaned = gemini_client.normalize_response(response)
            final_clean = gemini_client.strip_json_noise(cleaned)
            return final_clean if final_clean else response
        
        return None
    except Exception as e:
        print(f"Error generating content: {e}")
        return None


def _type_into_document(content, delay=0.01):
    """Type content into the active document using pyautogui
    
    Args:
        content: Text to type
        delay: Delay between keystrokes (lower = faster)
    """
    try:
        # Make sure the document window is in focus
        time.sleep(0.5)
        
        # Type the content character by character
        # pyautogui.typewrite is slow for large text, so we use write()
        for char in content:
            if char == '\n':
                pyautogui.press('enter')
            elif char == '\t':
                pyautogui.press('tab')
            else:
                pyautogui.typewrite(char, interval=delay)
            time.sleep(0.01)
        
        return True
    except Exception as e:
        print(f"Error typing into document: {e}")
        # Fall back to using clipboard
        try:
            return _type_using_clipboard(content)
        except:
            return False


def _type_using_clipboard(content):
    """Alternative method: Use clipboard to paste content
    
    This is more reliable for large text
    """
    try:
        import subprocess
        
        # Copy content to clipboard
        process = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
        process.communicate(content.encode('utf-8'))
        process.wait()
        
        # Paste from clipboard
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'v')
        
        return True
    except Exception as e:
        print(f"Error using clipboard: {e}")
        return False
