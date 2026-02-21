# 🤖 EchoMind AI Voice Assistant - Complete User Guide

Welcome to **EchoMind**! This document provides the full list of commands and features available in your AI voice assistant.

---

## 🎙️ Core Interaction & Feedback
*   **Visual Feedback**: EchoMind displays "Speaking...", "Listening...", and "You said: ..." in the terminal. 👁️
*   **Proactive Interaction**: After performing an action, EchoMind will ask: *"I am listening to you.... please tell me what to do next"* to stay ready for your next command. 🗣️
*   **Non-Blocking Listening**: The assistant stays active and responsive even when you are using other apps like Chrome or YouTube. 🔄
*   **Manners & Help**: Say "Hello", "Thank you", or "What can you do?" for general assistance. 😊

---

## 📝 Document & File Writing (Advanced)
EchoMind can automatically write stories, lyrics, and essays for you in real-time.

*   **Create New Full Document**: 📄
    *   *"Open notebook and write a story about a dragon."*
    *   *"Open word and write a poem about nature."*
*   **Smart Continuation (Multi-Text)**: 📑
    *   *"In the **current** notepad, write a song lyrics for 'Bole Chudiyan'."*
    *   *Note: EchoMind will automatically add a **5-line gap** before starting the new text!*
*   **Unicode Support (Bengali/Hindi)**: 🌍
    *   EchoMind now supports writing in native scripts like **Bengali** or **Hindi**. It uses a robust clipboard method to ensure non-English characters show up perfectly in your document.
*   **Accurate Lyric Research**: 🎶
    *   If you ask for a specific song, EchoMind performs background research to ensure it writes the **actual lyrics**, not just generic text.

---

## 🚀 Application & Window Management
*   **Open Apps**: "Open Chrome", "Launch Notepad", "Start Word", "Open Camera". 📥
*   **Close Apps/Tabs**: 📤
    *   "Close Chrome", "Close Word", "Close Camera".
    *   "Close YouTube" (Closes the specific video tab).
    *   "Close the current tab" / "Close this tab".
*   **Browser Navigation**: 📑
    *   "Next tab" / "Previous tab" (Eyes-free navigation).
    *   "Move to 1st tab" / "Go to last tab".
*   **System Folders**: 📂
    *   "Open Desktop", "Open Downloads", "Open Documents".

---

## ⚙️ System Controls
*   **Volume**: "Volume up", "Volume down", "Mute". 🔊
*   **Brightness**: "Set brightness to 70%", "Brightness up". ☀️
*   **Battery Status**: "Check battery status", "Is it charging?". 🔋
*   **Hotkeys**: ⌨️
    *   **F1**: Opens the Emoji Picker.
    *   **F5**: Unmutes the assistant/system.

---

## 📂 Developer Guide: Working Principles
A quick recap of how EchoMind works under the hood:

*   `main_refactored.py`: The central hub that orchestrates the assistant and routes voice commands to specialized handlers. 🤖 Hub
*   `config/settings.py`: The configuration center where global variables like OS type, API keys, and application maps are managed. ⚙️ Config
*   `handlers/app_handler.py`: Specialized module for finding and launching desktop applications like Chrome, Word, or any installed software on your system. 📥 Opener
*   `handlers/close_app_handler.py`: Responsible for safely terminating running applications or closing specific browser tabs using task management and hotkeys. 📤 Closer
*   `handlers/music_handler.py`: Handles your entertainment by searching for songs on YouTube and opening them directly in your browser. 🎶 Music
*   `handlers/file_writing_handler.py`: Automatically opens Notepad or Word and uses AI to generate and type text, stories, or lyrics for you. 📝 Writer
*   `handlers/web_handler.py`: Manages web searches, website opening, and WhatsApp Web interactions to keep you connected to the internet. 🌐 Web
*   `handlers/system_folder_handler.py`: Your personal file navigator for opening system folders like Downloads or Desktop and managing local disk drives. 📂 Folders
*   `handlers/weather_handler.py`: Fetches real-time weather information for any city using the OpenWeatherMap API and speaks the forecast. 🌤️ Weather
*   `handlers/battery_handler.py`: Monitors your system's energy levels in the background and warns you when the battery is low or charging status changes. 🔋 Battery
*   `handlers/time_handler.py`: A simple utility that tells you the current time whenever you need a quick check on your schedule. ⏰ Time
*   `handlers/date_handler.py`: Keeps you updated on the current calendar date and day of the week with shared voice feedback. 📅 Date
*   `handlers/brightness_handler.py`: Adjusts your screen brightness levels automatically through system commands or keyboard simulation. ☀️ Brightness
*   `handlers/volume_handler.py`: Controls your system's audio levels, allowing you to mute, unmute, or set specific volume percentages by voice. 🔊 Volume
*   `handlers/tab_navigation_handler.py`: Allows eyes-free browser navigation by switching between open tabs or moving to the next/previous page using shortcuts. 📑 Tabs
*   `handlers/text_input_handler.py`: Activates a manual typing mode for moments when you prefer to interact via keyboard instead of voice. ⌨️ Text Mode
*   `handlers/usb_detection_handler.py`: Watches for newly connected or removed USB devices in the background and alerts you immediately. 🔌 USB
*   `handlers/greeting_handler.py`: Manages friendly interactions like hellos and welcomes to make the assistant feel more conversational and alive. 👋 Hello
*   `handlers/thank_you_handler.py`: Responds politely to your thanks and appreciation, maintaining a helpful and friendly persona. 😊 Manners
*   `handlers/personal_handler.py`: Answers questions about its creator (Babin Bid) and its own identity to build a personal connection. 👨‍💻 Personal
*   `handlers/exit_handler.py`: Gracefully shuts down the assistant, stops background threads, and says goodbye when you're finished. 🚪 Exit
*   `utils/voice_io.py`: The ears and voice of the system, handling speech recognition and text-to-speech across different platforms. 🎙️ Voice
*   `utils/text_processing.py`: Cleans up and normalizes spoken text, converting symbols and formatting commands for better AI understanding. 🧹 Text
*   `utils/logger.py`: Keeps a detailed record of all interactions and errors in a structured log file for future reference and debugging. 📓 Logs
*   `clients/gemini_client.py`: The primary "AI brain" that processes complex questions using Google Gemini with an automatic failover to other providers. 🧠 Brain

---

### 💡 Pro Tip:
EchoMind is powered by **Google Gemini**. If it doesn't have a local command for your request, it uses its "AI Brain" to find the best possible answer for you! 🚀
