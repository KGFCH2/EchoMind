# 🤖 EchoMind — Complete User Guide & Documentation

> Everything you need to know about how my voice assistant works, what it can do, and how I built it.

---

## 🎙️ How It Feels to Use

When I run EchoMind, it greets me based on the time of day and immediately starts listening. I speak naturally, and it responds — either by performing an action (opening an app, searching the web) or by answering my question using its AI brain. Here's what I see in my terminal:

```
Speaking: Good evening! I am EchoMind, your voice assistant. How can I help you?
Listening...
You said: open chrome
Speaking: Opening chrome
Speaking: I am listening to you.... please tell me what to do next
Listening...
```

*   **👁️ Visual Feedback**: I always know what's happening — "Speaking...", "Listening...", "You said: ..." appear in real time.
*   **🗣️ Proactive Follow-up**: After every action, my assistant says *"I am listening to you.... please tell me what to do next"* so I never wonder if it's still active.
*   **🔄 Non-Blocking**: Even when I switch to Chrome or YouTube, EchoMind keeps listening in the background. It never stops.
*   **😊 Personality**: I can say "Hello", "Thank you", or ask personal questions. It responds warmly.

---

## 📝 Document & File Writing

This is one of my favorite features. I can open Notepad or Word and have the AI generate and type content for me automatically.

### ✍️ Creating a New Document
*   *"Open notebook and write a story about a dragon."* 📄
*   *"Open word and write a poem about nature."* 📄

### 📑 Adding More Content to the Same Document
If my document is already open, I don't need to say "open" again. I just say:
*   *"In the **current** notepad, write a Bengali song."*
*   *"Write a poem about love in the notepad."*

My assistant will automatically add a **5-line gap** before the new content so each piece stays visually separated.

### 🌍 Unicode & Multi-Language Support
I built a special clipboard method using PowerShell so that **Bengali**, **Hindi**, and other non-English scripts display perfectly. Earlier, characters were invisible because `pyautogui.typewrite()` only supports ASCII. Now it copies via clipboard and pastes — works flawlessly.

### 🎶 Accurate Song Lyrics
When I ask for a specific song (e.g., *"Write the Bole Chudiyan song from Kabhi Khushi Kabhie Gham"*), my assistant sends a research-focused prompt to the AI, requesting the **actual lyrics** instead of generating random text.

---

## 🚀 Application & Window Management

### 📥 Opening Apps
*   *"Open Chrome"*, *"Launch Notepad"*, *"Start Word"*, *"Open Camera"*.

### 📤 Closing Apps & Tabs
I improved the closing logic so it handles specific scenarios properly:
*   *"Close Chrome"* — Terminates the entire Chrome process.
*   *"Close Camera"* — Kills the Windows Camera app specifically.
*   *"Close YouTube"* — Smart enough to close just the YouTube **tab**, not the whole browser.
*   *"Close the current tab"* / *"Close this tab"* — Sends Ctrl+W to close whatever tab is active.

### 📑 Browser Tab Navigation
I can navigate between my open browser tabs completely hands-free:
*   *"Next tab"* — Moves to the right tab (Ctrl+Tab). ➡️
*   *"Previous tab"* — Moves to the left tab (Ctrl+Shift+Tab). ⬅️
*   *"Move to 1st tab"* / *"Go to 3rd tab"* — Jumps directly (Ctrl+1, Ctrl+3). 🔢
*   *"Go to last tab"* — Jumps to the final tab (Ctrl+9). 🔚

### 📂 System Folders & Drives
*   *"Open Desktop"*, *"Open Downloads"*, *"Open Documents"*.
*   *"Open Drive C"* / *"Open Drive D"*.
*   *"Eject Drive E"* — Safely ejects external drives.

---

## 🌐 Web, Music & Search

### 🔍 Web Search
*   *"Search for Python tutorials on Chrome"*
*   *"Google latest news"*

### 🎵 Music & YouTube
*   *"Play Shape of You on YouTube"*
*   *"Search for Arijit Singh songs"*

### 📱 Social & Communication
*   *"Open WhatsApp Web"*
*   *"Open Instagram"*, *"Open YouTube"*, *"Open GitHub"*.

---

## ⚙️ System Controls

| Command | What It Does | Emoji |
|---|---|---|
| *"Volume up"* / *"Volume down"* | Adjusts system volume | 🔊 |
| *"Mute"* | Mutes the system | 🔇 |
| *"Set brightness to 70%"* | Sets screen brightness | ☀️ |
| *"Check battery status"* | Reports battery level & charging state | 🔋 |
| Press **F1** | Opens the Emoji Picker (Win+.) | 😀 |
| Press **F5** | Unmutes the system | 🔈 |

---

## 🛑 Exiting EchoMind
*   *"Exit"*, *"Goodbye"*, or *"Terminate"*. 🚪
*   The assistant will say "Goodbye!" and gracefully shut down all background threads.

---

## 🏗️ How I Built It — Developer Recap

I designed EchoMind with a **handler-based architecture**. Every feature lives in its own file, and the main loop just routes commands to the right handler. Here's a 2-sentence summary for every file:

### 🤖 Core
*   `main_refactored.py` — This is my central command router. It listens for voice input, matches it against all registered handlers, and falls back to Gemini AI if nothing matches. 🎛️
*   `config/settings.py` — I store all my global configuration here, including OS detection, API key references, website URL maps, and process name mappings. ⚙️

### 🧠 AI Clients
*   `clients/gemini_client.py` — My primary AI brain. It calls Google Gemini's API, handles rate-limit fallback to Groq, parses JSON responses, and cleans up the output for natural speech. 🧠
*   `clients/groq_client.py` — My backup AI provider. If Gemini hits its rate limit (HTTP 429), this client takes over automatically using Groq's Llama model. 🔄

### 🧩 Handlers
*   `handlers/app_handler.py` — I wrote this to find and launch any desktop application. It searches common installation paths on Windows and Linux to locate executables. 📥
*   `handlers/close_app_handler.py` — This handles closing apps and tabs. It uses `taskkill` for full app termination and `Ctrl+W` for closing individual browser tabs. 📤
*   `handlers/music_handler.py` — My music player. It scrapes YouTube search results to find the top video URL and opens it directly in my browser. 🎶
*   `handlers/file_writing_handler.py` — I'm proud of this one. It opens Notepad/Word, generates content via AI, and types it into the document. I added Unicode clipboard support for Bengali/Hindi. ✍️
*   `handlers/web_handler.py` — This manages all web-related actions: Google searches, opening specific websites, and launching WhatsApp Web. 🌐
*   `handlers/system_folder_handler.py` — My file system navigator. It opens Windows folders like Downloads, Desktop, or specific drives, and can safely eject USB drives. 📂
*   `handlers/weather_handler.py` — Fetches live weather data from OpenWeatherMap and speaks the temperature, humidity, and conditions for any city I ask about. 🌤️
*   `handlers/simple_weather_handler.py` — A lighter version of the weather handler that catches simple queries like just saying a city name. 🌡️
*   `handlers/battery_handler.py` — Runs a background thread that monitors my battery level. It warns me at 20% and announces when charging starts or stops. 🔋
*   `handlers/usb_detection_handler.py` — Watches for USB devices being plugged in or removed and announces the change immediately. 🔌
*   `handlers/time_handler.py` — A simple handler that tells me the current time when I ask. ⏰
*   `handlers/date_handler.py` — Similar to time, but for the calendar date and day of the week. 📅
*   `handlers/brightness_handler.py` — Controls my screen brightness using system commands or simulated keyboard input. ☀️
*   `handlers/volume_handler.py` — Adjusts my system volume — I can say "volume up", "volume down", or set a specific percentage. 🔊
*   `handlers/tab_navigation_handler.py` — My hands-free browser navigator. It sends Ctrl+Tab, Ctrl+Shift+Tab, or Ctrl+[number] to switch between tabs. 📑
*   `handlers/text_input_handler.py` — If I ever prefer typing over speaking, this activates a manual text input mode in the terminal. ⌨️
*   `handlers/emoji_handler.py` — Triggers the Windows Emoji Picker (Win+.) when I press F1 or say "open emoji". �
*   `handlers/greeting_handler.py` — Makes EchoMind feel human. It responds to "Hello", "Hi", and friendly greetings with warmth. 👋
*   `handlers/thank_you_handler.py` — I taught it manners. It replies politely when I say "Thank you" or "Thanks". 😊
*   `handlers/personal_handler.py` — It knows who created it and can answer questions about its identity or purpose. 👨‍💻
*   `handlers/resume_handler.py` — A personal utility I built to quickly open my resume file from a specific path on my system. �
*   `handlers/exit_handler.py` — Handles graceful shutdown. It stops all background threads, says "Goodbye!", and exits the loop cleanly. 🚪

### 🛠️ Utilities
*   `utils/voice_io.py` — The ears and mouth of EchoMind. It handles microphone input via `speech_recognition` and text-to-speech output via platform-specific tools. 🎙️
*   `utils/text_processing.py` — Cleans up spoken input by converting symbols, removing noise, and formatting questions with proper punctuation. 🧹
*   `utils/time_utils.py` — A small utility that generates time-based greetings like "Good morning" or "Good evening". 🕐
*   `utils/logger.py` — Every interaction gets logged to `logs/assistant.jsonl` so I can review conversations and debug issues later. 📓
*   `utils/weather.py` — Calls the OpenWeatherMap API and returns structured weather data that my handlers can speak. 🌦️

---

### 💡 Pro Tip:
I power EchoMind with **Google Gemini** as my primary AI. If no local handler matches a command, it gets forwarded to Gemini, making the assistant capable of answering virtually anything. 🚀
