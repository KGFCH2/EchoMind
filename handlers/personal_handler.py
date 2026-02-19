"""Personal questions handler"""
import re
from utils.voice_io import speak
from utils.logger import log_interaction

# Tech stack information
TECH_STACK = [
    "Python 3.8+",
    "Google Gemini 2.0-Flash API",
    "Google Speech Recognition",
    "pyttsx3 for text-to-speech",
    "Windows Task Scheduling",
    "Modular Architecture with 16+ handlers",
    "JSONL-based logging",
    "RESTful API integration",
    "Streaming response handling",
    "JSON payload construction"
]

CREATOR_INFO = {
    'name': 'Babin Bid',
    'tech_stack': ', '.join(TECH_STACK[:5])  # First 5 for brevity
}

def handle_personal_questions(command):
    """Handle personal questions about the assistant
    
    Only handle if there's no other explicit intent (translate, convert, language, etc)
    This ensures queries like "who are you in Bengali" go to Gemini for translation
    """
    # Check if this is about the creator
    if re.search(r'\b(who\s+is|do\s+you\s+know)\s+(babin|b a b i n|babin\s+bid)\b', command, re.IGNORECASE):
        if re.search(r'\bwho\s+is\b', command, re.IGNORECASE):
            # "Who is Babin?" or "Who is Babin Bid?"
            response = (f"Babin Bid is my creator and the developer of EchoMind AI. "
                       f"He built me using {CREATOR_INFO['tech_stack']} and many other technologies "
                       f"to create a voice assistant that can understand and respond to commands.")
        else:
            # "Do you know Babin?" or "Do you know Babin Bid?"
            response = (f"Yes, I know him! Babin Bid is my creator. He developed me (EchoMind AI) using "
                       f"{CREATOR_INFO['tech_stack']}, Google Speech Recognition, and other modern technologies. "
                       f"Because of him, I can understand your voice commands and provide intelligent responses.")
        
        speak(response)
        log_interaction(command, response, source="local")
        return True
    
    # Check if there are other explicit intents that override personal questions
    # Include language names to catch queries like "who are you in bengali"
    override_keywords = r'\b(translate|convert|language|meaning|definition|spell|pronounce|write|encode|decode|in\s+(bengali|hindi|spanish|french|german|gujarati|tamil|telugu|kannada|marathi|punjabi|urdu|arabic|chinese|japanese|korean|russian|portuguese|italian|thai|vietnamese))\b'
    if re.search(override_keywords, command, re.IGNORECASE):
        # Don't handle personal questions if user is asking for translation/conversion
        return False
    
    if re.search(r'\b(how are you|how do you do)\b', command, re.IGNORECASE):
        speak("I'm doing well, thank you! How can I assist you?")
        log_interaction(command, "I'm doing well, thank you! How can I assist you?", source="local")
        return True
    elif re.search(r'\b(your name|who are you|what are you)\b', command, re.IGNORECASE):
        speak("I am EchoMind AI, your voice assistant.")
        log_interaction(command, "I am EchoMind AI, your voice assistant.", source="local")
        return True
    
    return False
