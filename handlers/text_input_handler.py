"""Text input handler - allows manual text input when "text" keyword is detected"""
import re
import os
from utils.voice_io import speak
from utils.logger import log_interaction
import gemini_client
from handlers.personal_handler import handle_personal_questions
from handlers.exit_handler import handle_exit
from handlers.thank_you_handler import handle_thank_you


def handle_text_input(command):
    """Handle text/text mode commands for manual input
    
    Detects keywords like:
    - "I want to give you a text message"
    - "Open text mode"
    - "Text"
    - "Text input"
    - "Give me text mode"
    
    When detected, prompts user to type their question manually
    """
    # Keywords that trigger text mode
    text_keywords = r'\b(text|text\s+mode|text\s+input|text\s+message|manual\s+input)\b'
    
    if not re.search(text_keywords, command, re.IGNORECASE):
        return False
    
    # Check if this is actually a request for text mode vs just mentioning the word "text"
    # Filter out commands like "text message to" which should go to messaging
    if re.search(r'\b(?:send|message|to|write)\s+(?:a\s+)?(?:text|message)\b', command, re.IGNORECASE):
        # This might be a messaging command, not text mode
        # Only handle if it explicitly says "text mode" or "text input"
        if not re.search(r'\btext\s+(?:mode|input)\b', command, re.IGNORECASE):
            return False
    
    try:
        # Announce text mode activation
        speak("Entering text mode. Please type your question or command.")
        print("\n" + "="*60)
        print("TEXT MODE ACTIVATED")
        print("="*60)
        
        # Prompt user for input
        user_text = input("\n📝 Type your question (or press Enter to skip): ").strip()
        
        print("="*60 + "\n")
        
        if not user_text:
            speak("Text input cancelled.")
            log_interaction(command, "Text mode entered but cancelled", source="text_input")
            return True
        
        # Log the text input
        log_interaction(command, f"Text input: {user_text}", source="text_input")
        
        # Process the typed text with Gemini
        speak(f"Processing your input: {user_text}")
        
        # Check for exit commands FIRST (highest priority)
        if handle_exit(user_text):
            speak("Goodbye!")
            log_interaction(user_text, "Exit via text mode", source="text_input_exit")
            return "exit"  # Signal to exit the main loop
        
        # Check for thank you
        if handle_thank_you(user_text):
            # Thank you handler already spoke the response
            return True
        
        # First check if it's a personal question (e.g., "who is babin bid?")
        if handle_personal_questions(user_text):
            # Personal handler already spoke the response
            return True
        
        # Get response from Gemini if not a personal question
        response = _process_text_input(user_text)
        
        if response:
            print(f"\n📤 Response: {response}\n")
            speak(response)
            log_interaction(user_text, response, source="text_input_gemini")
        else:
            speak("Sorry, I couldn't generate a response.")
            log_interaction(user_text, "No response generated", source="text_input")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\nText mode cancelled by user.")
        speak("Text mode cancelled.")
        log_interaction(command, "Text mode cancelled", source="text_input")
        return True
    except Exception as e:
        speak("Sorry, there was an error in text mode.")
        print(f"Error in text input handler: {e}")
        log_interaction(command, f"Error: {e}", source="text_input")
        return False


def _process_text_input(text_input):
    """Process the manually typed text through Gemini
    
    Args:
        text_input: The text typed by user
    
    Returns:
        Response from Gemini API
    """
    try:
        stream_flag = os.getenv("GEMINI_API_STREAM", "").lower() in ("1", "true", "yes")
        
        if stream_flag:
            try:
                # Try streaming first
                gen = gemini_client.stream_generate(text_input)
                
                # Collect all chunks
                chunks = []
                for chunk in gen:
                    if chunk:
                        chunks.append(chunk)
                
                if chunks:
                    response = " ".join(chunks)
                    # Clean the response
                    cleaned = gemini_client.normalize_response(response)
                    final_response = gemini_client.strip_json_noise(cleaned)
                    return final_response if final_response else response
                else:
                    # Fallback to blocking if streaming returns nothing
                    return _get_blocking_response(text_input)
            except Exception as e:
                print(f"Streaming error: {e}")
                return _get_blocking_response(text_input)
        else:
            return _get_blocking_response(text_input)
    
    except Exception as e:
        print(f"Error processing text input: {e}")
        return None


def _get_blocking_response(text_input):
    """Get response using blocking API call
    
    Args:
        text_input: The text to process
    
    Returns:
        Response from Gemini API
    """
    try:
        response = gemini_client.generate_response(text_input)
        if response:
            cleaned = gemini_client.normalize_response(response)
            final_response = gemini_client.strip_json_noise(cleaned)
            return final_response if final_response else response
        return None
    except Exception as e:
        print(f"Error in blocking call: {e}")
        return None
