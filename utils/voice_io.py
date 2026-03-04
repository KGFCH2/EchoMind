"""Text-to-speech and voice input utilities"""
import subprocess
import speech_recognition as sr
from config.settings import OS
import sounddevice as sd
import typing

class SoundDeviceMicrophone(sr.AudioSource):
    """Custom microphone wrapper to substitute PyAudio with sounddevice."""
    def __init__(self, device_index=None, sample_rate=None, chunk_size=1024):
        self.device_index = device_index
        self.format = 8
        self.SAMPLE_WIDTH = 2
        if sample_rate is None:
            device_info = sd.query_devices(device_index, 'input')
            self.SAMPLE_RATE = int(device_info['default_samplerate'])
        else:
            self.SAMPLE_RATE = sample_rate
        self.CHUNK = chunk_size
        self.audio: typing.Any = None
        self.stream: typing.Any = None

    def __enter__(self):
        assert self.stream is None, "This audio source is already inside a context manager"
        self.audio = sd.RawInputStream(
            samplerate=self.SAMPLE_RATE,
            channels=1,
            dtype='int16',
            blocksize=self.CHUNK,
            device=self.device_index
        )
        self.audio.start()
        
        class StreamWrapper:
            def __init__(self, raw_stream):
                self.raw_stream = raw_stream
            def read(self, size):
                data, overflow = self.raw_stream.read(size)
                return bytes(data)
                
        self.stream = StreamWrapper(self.audio)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.audio:
            self.audio.stop()
            self.audio.close()
        self.stream = None
        self.audio = None

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
                    pass
        else:
            pass
    except Exception:
        pass


def speak_stream(chunks, min_buffer: int = 200, pause_on_punctuation: bool = False):
    """Assemble an iterable/generator of text chunks into complete text.

    Behavior:
    - Accumulates incoming chunks into a buffer
    - Returns the complete assembled text
    - Does NOT print or speak (caller is responsible for that)

    This ensures clean single output without duplication.
    """
    buf: "list[str]" = []

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
    """Function to listen to user's voice command using sounddevice + Google Speech Recognition"""
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
        with SoundDeviceMicrophone() as source:
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
