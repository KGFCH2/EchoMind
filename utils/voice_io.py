"""Text-to-speech and voice input utilities"""
import subprocess
import speech_recognition as sr
from config.settings import OS

def speak(text):
    """Cross-platform text-to-speech"""
    # Strip Markdown formatting (asterisks, bold markers) before speaking
    clean_text = text.replace("**", "").replace("*", "").replace("__", "").replace("_", "")
    print(f"Speaking: {clean_text}")
    try:
        if OS == "windows":
            subprocess.run(["powershell", "-c", f'(New-Object -ComObject SAPI.SpVoice).Speak("{clean_text}")'], capture_output=True)
        elif OS == "darwin":  # macOS
            subprocess.run(["say", clean_text], capture_output=True)
        elif OS == "linux":
            try:
                subprocess.run(["espeak", clean_text], capture_output=True)
            except FileNotFoundError:
                try:
                    subprocess.run(["festival", "--tts"], input=clean_text.encode(), capture_output=True)
                except FileNotFoundError:
                    # print(f"TTS not available on this Linux system. Text: {clean_text}")
                    pass
        else:
            # print(f"TTS not supported on {OS}. Text: {clean_text}")
            pass
    except Exception:
        # Silently fail or log to file instead
        pass


def speak_stream(chunks, min_buffer: int = 200, pause_on_punctuation: bool = False):
    """Assemble an iterable/generator of text chunks into complete text.

    Behavior:
    - Accumulates incoming chunks into a buffer
    - Returns the complete assembled text
    - Does NOT print or speak (caller is responsible for that)

    This ensures clean single output without duplication.
    """
    buf = []

    for c in chunks:
        if not c:
            continue
        # ensure chunk is a string
        part = str(c)
        buf.append(part)

    # Assemble final text
    final_text = "".join(buf).strip()
    
    return final_text


def listen():
    """Function to listen to user's voice command"""
    recognizer = sr.Recognizer()
    attempts = 3
    ambient_duration = 1.5
    listen_timeout = 8
    phrase_time_limit = 12

    try:
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 1.2
    except Exception:
        pass

    for attempt in range(attempts):
        with sr.Microphone() as source:
            print("Listening...")
            try:
                recognizer.adjust_for_ambient_noise(source, duration=ambient_duration)
            except Exception:
                pass

            try:
                audio = recognizer.listen(source, timeout=listen_timeout, phrase_time_limit=phrase_time_limit)
            except sr.WaitTimeoutError:
                print("Listening timed out waiting for phrase.")
                if attempt == attempts - 1:
                    speak("I didn't hear anything. Could you please repeat?")
                continue

        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            print("Speech not recognized (UnknownValueError)")
            if attempt == attempts - 1:
                speak("Sorry, I didn't understand that. Could you repeat?")
            continue
        except sr.RequestError:
            speak("Sorry, my speech service is down.")
            break

    # Non-blocking check for typed input (only if user explicitly wants it)
    # Removing mandatory blocking input to keep assistant "Always On" hands-free
    return ""
