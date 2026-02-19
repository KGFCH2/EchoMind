"""
EchoMind AI - Main entry point for the voice assistant
This refactored version uses modular architecture for better maintainability
"""
import os
import time
from dotenv import load_dotenv

# Load environment variables BEFORE importing other modules
load_dotenv()

# Import all handlers
from handlers.thank_you_handler import handle_thank_you
from handlers.greeting_handler import handle_greeting
from handlers.time_handler import handle_time
from handlers.date_handler import handle_date
from handlers.simple_weather_handler import handle_simple_city_weather
from handlers.weather_handler import handle_weather
from handlers.web_handler import handle_browser_search, handle_website_opening, handle_whatsapp_web
from handlers.file_handler import handle_file_opening
from handlers.file_writing_handler import handle_file_writing
from handlers.app_handler import handle_app_opening
from handlers.personal_handler import handle_personal_questions
from handlers.text_input_handler import handle_text_input
from handlers.brightness_handler import handle_brightness
from handlers.resume_handler import handle_resume_opening
from handlers.close_app_handler import handle_app_closing
from handlers.tab_navigation_handler import handle_tab_navigation
from handlers.system_folder_handler import handle_system_folder_opening
from handlers.music_handler import handle_play_music, handle_play_on_youtube
from handlers.exit_handler import handle_exit
from handlers.battery_handler import handle_battery_status, start_battery_monitoring, stop_battery_monitoring
from handlers.usb_detection_handler import handle_usb_detection, start_usb_monitoring, stop_usb_monitoring
from handlers.volume_handler import handle_volume

# Import utilities
from utils.voice_io import speak, listen, speak_stream
from utils.text_processing import convert_spoken_symbols, is_symbol_only, ensure_question_mark_if_question
from utils.time_utils import get_greeting
from utils.logger import log_interaction

# Import specific functions for global hotkeys
from handlers.emoji_handler import open_emoji, handle_emoji_mode
from handlers.volume_handler import press_f5_key

# Import Gemini client
import gemini_client


def route_command(command):
    """Route command to appropriate handler"""
    handlers = [
        ("Text input", handle_text_input),
        ("Thank you", handle_thank_you),
        ("Greeting", handle_greeting),
        ("Emoji mode", handle_emoji_mode),
        ("Time", handle_time),
        ("Date", handle_date),
        ("Resume opening", handle_resume_opening),  # NEW - Resume file handler
        ("USB detection", handle_usb_detection),
        ("Browser search", handle_browser_search),
        ("Website opening", handle_website_opening),
        ("Simple city weather", handle_simple_city_weather),
        ("Weather", handle_weather),
        ("WhatsApp", handle_whatsapp_web),
        ("Battery status", handle_battery_status),
        ("Volume control", handle_volume),
        ("File writing", handle_file_writing),
        ("Music (YouTube play)", handle_play_on_youtube),
        ("Music (play)", handle_play_music),
        ("File opening", handle_file_opening),
        ("System folder opening", handle_system_folder_opening),
        ("App opening", handle_app_opening),
        ("Personal questions", handle_personal_questions),
        ("Brightness control", handle_brightness),
        ("Tab navigation", handle_tab_navigation),
        ("App closing", handle_app_closing),
        ("Exit", handle_exit),
    ]
    
    for handler_name, handler in handlers:
        if handler_name == "Text input":
            # Special case for text input - can return "exit"
            result = handle_text_input(command)
            if result == "exit":
                return "exit"
            elif result:
                return "handled"
        elif handler_name == "Exit":
            # Special case for exit
            if handle_exit(command):
                return "exit"
        else:
            if handler(command):
                return "handled"
    
    return "not_handled"


def handle_gemini_fallback(command):
    """Handle unknown commands with Gemini
    
    Note: 'command' parameter should already have ? added if it's a question
    from the main() function's ensure_question_mark_if_question() call
    """
    try:
        # Use command as-is (already formatted with ? in main if needed)
        formatted_command = command
        
        stream_flag = os.getenv("GEMINI_API_STREAM", "").lower() in ("1", "true", "yes")
        if stream_flag:
            try:
                # Get streaming chunks
                gen = gemini_client.stream_generate(command)
                # Assemble complete response without printing
                final_text = speak_stream(gen)
                
                if not final_text or not final_text.strip():
                    print(f"DEBUG: Empty response from stream_generate for: {command}")
                    # Try blocking call as fallback
                    response = gemini_client.generate_response(command)
                    if response and "trouble" not in response.lower():
                        print(response)
                        speak(response)
                        log_interaction(formatted_command, response, source="gemini_fallback")
                    else:
                        speak("Sorry, I couldn't generate a response.")
                        log_interaction(formatted_command, "No response returned", source="gemini_stream")
                    return
                
                # Normalize and clean the complete response
                cleaned = gemini_client.normalize_response(final_text)
                final_clean = gemini_client.strip_json_noise(cleaned)
                
                # Use cleaned response if available, otherwise use final_text
                response_to_use = final_clean if final_clean else final_text
                if response_to_use and response_to_use.strip():
                    # Print and speak ONCE (no ? added to response)
                    print(response_to_use)
                    speak(response_to_use)
                    log_interaction(formatted_command, response_to_use, source="gemini_stream")
                else:
                    speak("Sorry, I couldn't generate a response.")
                    log_interaction(formatted_command, "No response returned", source="gemini_stream")
                
            except Exception as e:
                print(f"Streaming error: {e}")
                speak("Sorry, there was an error with streaming response.")
                log_interaction(formatted_command, f"Streaming error: {e}", source="gemini_stream")
        else:
            response = gemini_client.generate_response(command)
            if response:
                cleaned = gemini_client.normalize_response(response)
                final_clean = gemini_client.strip_json_noise(cleaned)
                
                if final_clean:
                    print(final_clean)
                    speak(final_clean)
                    log_interaction(formatted_command, final_clean, source="gemini")
                else:
                    print(response)
                    speak(response)
                    log_interaction(formatted_command, response, source="gemini")
            else:
                speak("Sorry, I couldn't generate a response.")
                log_interaction(formatted_command, "No response returned", source="gemini")
    except Exception as e:
        print(f"Gemini error: {e}")
        speak("Sorry, I couldn't process that right now.")
        log_interaction(command, f"Error: {e}", source="gemini")


def main():
    """Main function - voice assistant loop"""
    # Start background monitoring threads
    start_battery_monitoring()
    start_usb_monitoring()
    
    # Setup global hotkeys (F1 -> Win+. for emoji picker, F5 -> unmute)
    try:
        # Prefer pynput for global listening
        from pynput import keyboard as _pynput_keyboard

        def _on_press(key):
            try:
                if key == _pynput_keyboard.Key.f1:
                    print("Global hotkey: F1 pressed -> sending Win+. to open emoji picker")
                    try:
                        open_emoji()
                        log_interaction("F1 (hotkey)", "Win+. sent for emoji picker", source="hotkey")
                    except Exception as e:
                        print(f"Error opening emoji from hotkey: {e}")
                elif key == _pynput_keyboard.Key.f5:
                    print("Global hotkey: F5 pressed -> pressing F5 key for mute/unmute")
                    try:
                        press_f5_key()
                        log_interaction("F5 (hotkey)", "F5 key pressed for mute/unmute", source="hotkey")
                    except Exception as e:
                        print(f"Error pressing F5 from hotkey: {e}")
            except Exception:
                pass

        _listener = _pynput_keyboard.Listener(on_press=_on_press)
        _listener.daemon = True
        _listener.start()
        print("Global hotkey listener started (pynput)")
    except Exception:
        # Fallback to keyboard module if pynput is not available
        try:
            import keyboard as _keyboard

            try:
                def _f1_hotkey():
                    print('Hotkey f1 -> Win+. for emoji')
                    try:
                        open_emoji()
                        log_interaction('F1 (hotkey)', 'Win+. sent for emoji picker', source='hotkey')
                    except Exception as e:
                        print(f"F1 hotkey error: {e}")

                _keyboard.add_hotkey('f1', _f1_hotkey)
                _keyboard.add_hotkey('f5', lambda: (print('Hotkey f5 -> press F5 for mute/unmute'), press_f5_key(), log_interaction('F5 (hotkey)', 'F5 key pressed for mute/unmute', source='hotkey')))
                print("Global hotkey listener started (keyboard module)")
            except Exception as e:
                print(f"Failed to register hotkeys with keyboard module: {e}")
        except Exception:
            print("No global hotkey support available (pynput and keyboard modules missing)")
    
    greeting = get_greeting()
    speak(greeting)
    
    try:
        while True:
            # Listen for command
            command = listen()
            if not command:
                continue
            
            # Convert spoken symbols to actual punctuation marks
            command = convert_spoken_symbols(command)
            
            # Skip if command is only symbols
            if command and is_symbol_only(command):
                speak("I didn't catch a complete command. Could you please say something more?")
                continue
            
            # Format command with ? if it's a question (for logging)
            formatted_command = ensure_question_mark_if_question(command, None)
            
            # Route the command to handlers
            result = route_command(formatted_command)
            
            if result == "exit":
                speak("Goodbye!")
                break
            elif result == "handled":
                # Handler already processed the command
                time.sleep(0.5)  # Small delay to avoid rate limiting
                continue
            else:
                # No handler matched, try Gemini
                handle_gemini_fallback(formatted_command)
                time.sleep(0.5)  # Small delay between API calls to avoid rate limiting
    finally:
        # Stop background monitoring threads
        stop_battery_monitoring()
        stop_usb_monitoring()


if __name__ == "__main__":
    main()
