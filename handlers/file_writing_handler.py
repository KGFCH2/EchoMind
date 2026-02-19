"""File writing handler for Notepad, Word, etc."""
import re
import subprocess
import time
import os
import pyautogui
from config.settings import OS
from utils.voice_io import speak, listen
from utils.logger import log_interaction
import gemini_client


def handle_file_writing(command):
    """Handle writing content to files (Notepad, Word, etc.)
    
    Examples:
    - "Open notepad and write a story"
    - "Open word and write a bengali story in english"
    - "Open notepad and write a hindi poem"
    """
    if not re.search(r'\b(open|launch|start)\b.*\b(notepad|word|document|ms\s+word)\b.*\b(and\s+)?write\b', command, re.IGNORECASE):
        return False
    
    command_lower = command.lower()
    
    # Determine which app to open
    app_name = None
    if "notepad" in command_lower:
        app_name = "notepad"
    elif "word" in command_lower or "document" in command_lower:
        app_name = "word"
    else:
        return False
    
    # Extract the writing prompt
    write_prompt = None
    write_match = re.search(r'(?:and\s+)?write\s+(?:a\s+)?(?:.*?)(?:\s+(?:story|poem|essay|article|text))?$', command_lower)
    if write_match:
        write_prompt = write_match.group(0).replace("and write", "").replace("write", "").strip()
    
    # If no specific prompt, ask the user what to write
    if not write_prompt or len(write_prompt.strip()) < 3:
        write_prompt = "a creative story"
    
    try:
        # Open the application
        if OS == "windows":
            if app_name == "notepad":
                subprocess.Popen(["notepad.exe"])
            elif app_name == "word":
                subprocess.Popen(["winword.exe"])
        elif OS == "darwin":
            if app_name == "notepad":
                subprocess.Popen(["open", "-a", "TextEdit"])
            elif app_name == "word":
                subprocess.Popen(["open", "-a", "Microsoft Word"])
        elif OS == "linux":
            if app_name == "notepad":
                subprocess.Popen(["gedit"])
            elif app_name == "word":
                subprocess.Popen(["libreoffice", "--writer"])
        
        speak(f"Opening {app_name}")
        
        # Wait for application to open
        time.sleep(3)
        
        # Generate content using Gemini
        speak(f"Generating {write_prompt}...")
        log_interaction(command, f"Opening {app_name} to write {write_prompt}", source="local")
        
        # Use Gemini to generate the content
        content = _generate_content(write_prompt)
        
        if content:
            speak("Writing to the document...")
            
            # Type the content into the open document
            # Use pyautogui to simulate typing
            _type_into_document(content)
            
            speak(f"Finished writing {write_prompt} to {app_name}")
            log_interaction(command, f"Wrote {write_prompt} to {app_name}", source="local")
            return True
        else:
            speak("Sorry, I couldn't generate the content.")
            return False
    
    except Exception as e:
        speak(f"Sorry, there was an error opening {app_name}.")
        print(f"File writing error: {e}")
        return False


def _generate_content(prompt):
    """Generate content using Gemini API"""
    try:
        # Make sure prompt is a complete request
        if not any(keyword in prompt.lower() for keyword in ['story', 'poem', 'essay', 'article', 'tale', 'paragraph']):
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
