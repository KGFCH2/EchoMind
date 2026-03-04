# 🤖 EchoMind — Complete User Guide & Documentation

> Everything you need to know about how my voice assistant works, what it can do, and how I built it.

---

## 🎙️ How It Feels to Use

When I run EchoMind, it greets me based on the time of day and immediately starts listening. I speak naturally, and it responds — either by performing an action (opening an app, searching the web) or by answering my question using its AI brain (powered by **Gemini** or **Groq**). Here's what I see in my terminal:

```text
Speaking: Good evening! I am EchoMind, your voice assistant. How can I help you?
Listening...
You said: open chrome
Speaking: Opening chrome
Speaking: I am listening to you.... please tell me what to do next
Listening...
```

* **👁️ Visual Feedback**: I always know what's happening — "Speaking...", "Listening...", "You said: ..." appear in real time.
* **🗣️ Smart Follow-up**: After performing specific actions (like opening an app or playing music), my assistant says *"I am listening to you.... please tell me what to do next"* so I know it's ready for the next task. For general questions, it stays silent and waits in the background.
* **🔄 Non-Blocking**: Even when I switch to Chrome or YouTube, EchoMind keeps listening in the background. It never stops.
* **😊 Personality**: I can say "Hello", "Thank you", or ask personal questions. It responds warmly.

---

## 📝 Document & File Writing

This is one of my favorite features. I can open Notepad or Word and have the AI generate and type content for me automatically.

### ✍️ Creating a New Document

* *"Open notebook and write a story about a dragon."* 📄
* *"Open word and write a poem about nature."* 📄

### 📑 Adding More Content to the Same Document

If my document is already open, I don't need to say "open" again. I just say:

* *"In the **current** notepad, write a Bengali song."*
* *"Write a poem about love in the notepad."*

My assistant will automatically add a **5-line gap** before the new content so each piece stays visually separated.

### 🌍 Unicode & Multi-Language Support

I built a special clipboard method using PowerShell so that **Bengali**, **Hindi**, and other non-English scripts display perfectly. Earlier, characters were invisible because `pyautogui.typewrite()` only supports ASCII. Now it copies via clipboard and pastes — works flawlessly.

### 🎶 Accurate Song Lyrics

When I ask for a specific song (e.g., *"Write the Bole Chudiyan song from Kabhi Khushi Kabhie Gham"*), my assistant sends a research-focused prompt to the AI, requesting the **actual lyrics** instead of generating random text.

---

## 🚀 Application & Window Management

### 📥 Opening Apps

* *"Open Chrome"*, *"Launch Notepad"*, *"Start Word"*, *"Open Camera"*.

### 📤 Closing Apps & Tabs

I improved the closing logic so it handles specific scenarios properly:

* *"Close Chrome"* — Terminates the entire Chrome process.
* *"Close Camera"* — Kills the Windows Camera app specifically.
* *"Close YouTube"* — Smart enough to close just the YouTube **tab**, not the whole browser.
* *"Close the current tab"* / *"Close this tab"* — Sends Ctrl+W to close whatever tab is active.

### 📑 Browser Tab Navigation

I can navigate between my open browser tabs completely hands-free:

* *"Next tab"* — Moves to the right tab (Ctrl+Tab). ➡️
* *"Previous tab"* — Moves to the left tab (Ctrl+Shift+Tab). ⬅️
* *"Move to 1st tab"* / *"Go to 3rd tab"* — Jumps directly (Ctrl+1, Ctrl+3). 🔢
* *"Go to last tab"* — Jumps to the final tab (Ctrl+9). 🔚

### 📂 System Folders & Drives

* *"Open Desktop"*, *"Open Downloads"*, *"Open Documents"*.
* *"Open Drive C"* / *"Open Drive D"*.
* *"Eject Drive E"* — Safely ejects external drives.

---

## 🌐 Web, Music & Search

### 🔍 Web Search

* *"Search for Python tutorials on Chrome"*
* *"Google latest news"*

### 🏏 Live Cricket Scores

* *"Live cricket score"*
* *"Cricket match score"*

### 🎵 Music & YouTube

* *"Play Shape of You on YouTube"*
* *"Search for Arijit Singh songs"*

### 📱 Social & Communication

* *"Open WhatsApp Web"*
* *"Open Instagram"*, *"Open YouTube"*, *"Open GitHub"*.

---

### 🔔 Smart Reminders

EchoMind can act as your personal assistant for tasks and time-sensitive alerts:

* *"Remind me at 9:48 PM"* — Sets a precise reminder. ⏰
* *"What are my reminders?"* — Lists all active pending reminders. 📋
* *"Cancel reminder for 10:00 PM"* — Removes a specific reminder from the list. 🗑️

---

## ⚙️ System Controls

| Command | What It Does | Emoji |
| :--- | :--- | :--- |
| *"Volume up"* / *"Volume down"* | Adjusts system volume | 🔊 |
| *"Mute"* | Mutes the system | 🔇 |
| *"Set brightness to 70%"* | Sets screen brightness | ☀️ |
| *"Check battery status"* | Reports battery level & charging state | 🔋 |
| Press **F1** | Opens the Emoji Picker (Win+.) | 😀 |
| Press **F5** | Unmutes the system | 🔈 |

---

## 🛑 Exiting EchoMind

* *"Exit"*, *"Goodbye"*, or *"Terminate"*. 🚪
* The assistant will say "Goodbye!" and gracefully shut down all background threads.

---

## 🏗️ The EchoMind Architecture: Full Documentation

I designed EchoMind with a modular, **handler-based architecture**. This means every feature is isolated in its own file, making the system easy to update and debug.

### 📂 1. Project Root Directories

* **`clients/`**: AI service wrappers for Gemini and Groq.
* **`config/`**: Global settings and platform mappings.
* **`handlers/`**: Core action modules (Muscle).
* **`utils/`**: Helper scripts for voice, logging, and data (Senses).
* **`logs/`**: Interaction history.
* **`models/`**: Offline speech models (e.g., Vosk).

---

### 📄 2. Root Files (The Core)

* **`main.py`**: The main entry point and terminal loop. 🎛️
* **`.env`**: (Hidden) Stores your secret API keys. 🔑
* **`.gitignore`**: Ignores sensitive files and large folders like `node_modules` and `models`. 🚫
* **`requirements.txt`**: Lists Python dependencies (added `fastapi`, `uvicorn`, `socketio`). 📦
* **`README.md`**: High-level project overview and setup guide. 📖
* **`INSTRUCTIONS.md`**: This exhaustive developer and user guide. 📖
* **`FUTURE_FEATURES.md`**: A roadmap of what I plan to build next for EchoMind. 🚀
* **`LICENSE`**: The legal license (MIT) governing how this code can be used. ⚖️

---

### 🧠 3. `clients/` — The AI Brains

* **`gemini_client.py`**: My primary AI provider. It manages the connection to Google Gemini 2.5, handles JSON parsing, and cleans up text for speech. 🧠
* **`groq_client.py`**: The fallback AI provider. If Gemini is busy or hits a rate limit, this automatically takes over using Llama 3 models via Groq. 🔄

---

### ⚙️ 4. `config/` — Global Settings

* **`settings.py`**: The central source of truth for all constants. It handles OS detection (Windows vs. Linux), defines app paths, and maps URLs for the web handler. ⚙️

---

### 🧩 5. `handlers/` — Every Individual Feature

* **`app_handler.py`**: Finds and launches any application (Chrome, Word, etc.) by searching Windows registry and system paths. 📥
* **`battery_handler.py`**: Monitors battery levels in the background and speaks alerts when charging starts or power is low. 🔋
* **`brightness_handler.py`**: Controls screen brightness using system-level WMI commands. ☀️
* **`close_app_handler.py`**: Closes entire applications (taskkill) or specific browser tabs (Ctrl+W) smartly. 📤
* **`cricket_handler.py`**: Scrapes and speaks real-time cricket scores using the CricketData API. 🏏
* **`date_handler.py`**: Answers questions about today's date, day, month, and year. 📅
* **`emoji_handler.py`**: Opens the Windows Emoji Picker (Win+.) for quick typing. 😀
* **`exit_handler.py`**: Shuts down EchoMind gracefully, stopping all threads and saying goodbye. 🚪
* **`file_handler.py`**: Logic for opening specific files or system folders like Desktop and Downloads. 📂
* **`file_writing_handler.py`**: The AI writer. It opens Notepad/Word, generates content, and types it in (supports Bengali/Unicode). ✍️
* **`greeting_handler.py`**: Handles polite opening conversations like "Hello" and "How are you?". 👋
* **`music_handler.py`**: Scrapes YouTube for any song name you say and plays the top result instantly. 🎶
* **`personal_handler.py`**: Contains identity info about EchoMind and its creator. 👨‍💻
* **`reminder_handler.py`**: The voice-activated reminder service. It sets and monitors background timers. 🔔
* **`resume_handler.py`**: A specific utility to immediately open the creator's resume file. 📄
* **`simple_weather_handler.py`**: A lightweight weather catcher for simple "City Name" queries. 🌡️
* **`system_folder_handler.py`**: Opens system drives (C:, D:) and handles safe USB ejection. 📂
* **`tab_navigation_handler.py`**: Hands-free browser control (Next Tab, Previous Tab, 1st Tab, etc.). 📑
* **`text_input_handler.py`**: Switches the assistant to "Text Mode" for those who prefer typing over speaking. ⌨️
* **`thank_you_handler.py`**: Responds politely to "Thank you" and "Thanks". 😊
* **`time_handler.py`**: Tells the current time with high precision. ⏰
* **`usb_detection_handler.py`**: Background thread that detects when USB devices are plugged in or unplugged. 🔌
* **`volume_handler.py`**: Controls system volume percentages and muting. 🔊
* **`weather_handler.py`**: Detailed weather reporter using the OpenWeatherMap API City/Country search. 🌤️
* **`web_handler.py`**: Manages Google searches, YouTube searches, and opening specific websites like WhatsApp Web. 🌐

---

### 🛠️ 6. `utils/` — Helper Utilities

* **`voice_io.py`**: The physical link to your hardware. It manages the Microphone (SoundDevice) and the Voice (TTsx3). 🎙️
* **`text_processing.py`**: Cleans up messy speech-to-text transcripts, adds punctuation, and converts symbols. 🧹
* **`time_utils.py`**: Small logic to determine if it's currently Morning, Afternoon, or Evening. 🕐
* **`logger.py`**: The recorder. It writes every conversation to a JSON log file so you can audit the AI's behavior. 📓
* **`weather.py`**: The backend API logic that fetches raw JSON data from weather servers. 🌦️

---

### 💡 Pro Tip

I power EchoMind with **Google Gemini** and **Groq** as its primary AI brains. If no local handler matches a command, it gets forwarded to one of these providers, making the assistant capable of answering virtually anything. 🚀
