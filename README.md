# EchoMind 🤖

> My AI-powered voice assistant that runs entirely from the terminal.

---

## ℹ️ About

I built **EchoMind** as a lightweight, modular AI voice assistant that lives in the terminal. It listens for my spoken commands, intelligently routes them to focused handler modules, and uses dual-provider AI support (**Google Gemini** and **Groq**) to answer anything that isn't handled locally. My goal was to create a hands-free assistant that feels alive, stays responsive, and helps me control my entire computer with just my voice.

---

## ✨ Key Features

- 🎙️ **Voice I/O** — I integrated speech-to-text and text-to-speech so the assistant can hear me and talk back.
- 🧩 **Modular Handlers** — I organized the codebase into small, focused handler modules inside `handlers/` (time, date, weather, files, music, system controls, app management, and more).
- 🌐 **AI Intelligence** — When no local handler matches, my assistant forwards the question to **Google Gemini** or **Groq** so it can answer virtually anything.
- 🏏 **Live Cricket Scores** — I can ask for real-time cricket scores and match status using the cricketdata API.
- 📝 **Smart Document Writing** — I can ask it to open Notepad or Word and write stories, poems, or even real song lyrics in any language, including Bengali and Hindi.
- 🔔 **Voice Reminders** — I can set, list, and cancel reminders by voice (e.g., *"remind me at 9:45 PM"*).
- 🔋 **Background Monitoring** — Battery level and USB device detection threads run silently in the background and alert me when something changes.
- ⌨️ **Global Hotkeys** — I set up F1 for the Emoji Picker and F5 for quick unmute.
- 🗣️ **Always Listening** — After every action, my assistant proactively says *"I am listening to you..."* so I never have to wonder if it's still active.

---

## 📦 Requirements

- Python 3.10+
- Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

I use a `.env` file to manage all my API keys and settings. Here are the important ones:

| Variable | Purpose |
| :--- | :--- |
| `GEMINI_API_KEY` | My primary AI brain (Google Gemini). |
| `GEMINI_API_ENDPOINT` | The API endpoint for Gemini. |
| `GEMINI_API_STREAM` | Set to `true` for streaming responses. |
| `GROQ_API_KEY` | Backup AI provider (auto-fallback). |
| `OPENWEATHER_API_KEY` | For real-time weather lookups. |
| `CRICKETDATA_API_KEY` | For real-time cricket scores. |

Example `.env` entry:

```dotenv
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

---

## 🌤️ Weather Information

I integrated OpenWeatherMap so I can ask about the weather in any city:

- *"What's the weather in London?"*
- *"Kolkata weather"*

To enable this, just set `OPENWEATHER_API_KEY` in your `.env`. Temperatures are returned in Celsius by default.

---

## ▶️ Running EchoMind

Start my assistant from the project root:

```bash
python main.py
```

It will greet you, then listen in a continuous loop. Speak naturally — it handles the rest. For a full list of what you can say, check out my **[INSTRUCTIONS.md](./INSTRUCTIONS.md)** 📖.

---

## 🏗️ Project Structure

Here's a quick overview of how I organized everything:

```text

EchoMind/
├── main.py      # 🤖 The main loop and command router
├── config/
│   └── settings.py          # ⚙️ All global settings and mappings
├── clients/
│   ├── gemini_client.py     # 🧠 Primary AI (Google Gemini)
│   └── groq_client.py       # 🔄 Backup AI (Groq Llama)
├── handlers/                # 🧩 One file per feature
│   ├── app_handler.py       # Open apps
│   ├── close_app_handler.py # Close apps & tabs
│   ├── music_handler.py     # YouTube music
│   ├── file_writing_handler.py  # AI-powered document writing
│   ├── web_handler.py       # Web search & browsing
│   ├── weather_handler.py   # Weather lookups
│   ├── tab_navigation_handler.py # Browser tab control
│   ├── reminder_handler.py  # Voice-activated reminders
│   └── ...more handlers
├── utils/
│   ├── voice_io.py          # 🎙️ Speech recognition & TTS
│   ├── text_processing.py   # 🧹 Text cleanup utilities
│   └── logger.py            # 📓 Interaction logging
├── INSTRUCTIONS.md           # 📖 Full user guide
└── .env                      # 🔑 API keys (not committed)
```

---

## 📝 Logs

I log every interaction and error to the `logs/` directory (e.g., `logs/assistant.jsonl`) so I can review conversations and debug issues later.

---

## ❗ Troubleshooting

| Problem | Solution |
| :--- | :--- |
| Voice I/O fails | Make sure your microphone and speakers are connected and dependencies are installed. |
| Weather lookups fail | Verify that `OPENWEATHER_API_KEY` is set and valid in your `.env`. |
| AI responses are missing | Ensure `GEMINI_API_KEY` and `GEMINI_API_ENDPOINT` are configured. |
| Bengali/Hindi text not showing | The clipboard method requires PowerShell on Windows. |

---

## 📄 License

This project is licensed under the **MIT License** — see `LICENSE` for details.
