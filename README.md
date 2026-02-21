# EchoMind 🤖

> EchoMind — an AI Voice Assistant through the terminal

ℹ️ About
-----

EchoMind is a lightweight, modular AI voice assistant that runs from the terminal. It listens for spoken commands, routes them to focused handler modules, and falls back to an LLM (via `clients/gemini_client.py`) when a command isn't handled locally.

✨ Key features
------------

- 🎙️ **Voice I/O**: speech-to-text and text-to-speech via `utils/voice_io.py`.
- 🧩 **Modular handlers**: small handler modules live in `handlers/` (time, date, weather, files, music, system controls, etc.).
- 🌐 **LLM fallback**: calls an external model using `clients/gemini_client.py` when needed (configure to enable).
- 🔋 **Background monitoring**: battery and USB monitoring threads run automatically.
- ⌨️ **Hotkeys**: optional global hotkey support (F1 / F5) if dependencies are installed.

📦 Requirements
------------

- Python 3.10+
- Install dependencies:

```bash
pip install -r requirements.txt
```

⚙️ Configuration
-------------

- Use a `.env` file (see `.env.example`) or set environment variables directly.
- Important variables:
  - `OPENWEATHER_API_KEY` — API key for OpenWeatherMap (required to enable weather features).
  - `GEMINI_API_KEY` — API key for LLM fallback (optional).
  - `GEMINI_API_ENDPOINT` / `GEMINI_API_STREAM` — optional LLM configuration.

🌤️ Weather information
-----------------

EchoMind supports weather lookups via OpenWeatherMap:

- Implementation: `utils/weather.py` fetches data from OpenWeatherMap and `handlers/weather_handler.py` and `handlers/simple_weather_handler.py` route weather queries.
- To enable: set `OPENWEATHER_API_KEY` in your `.env` or environment.

Example `.env` entry:

```dotenv
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

Example voice/text queries:

- "What's the weather in London?"
- "London weather"
- "Paris"

Note: Temperatures are returned in Celsius by default (see `utils/weather.py`). If you need a different unit, update the `units` parameter in the API request.

▶️ Running EchoMind
----------------

Start the assistant from the project root:

```bash
python main_refactored.py
```

The assistant speaks a greeting and listens in a loop; it will speak responses and run handlers for matched commands.

For a full list of supported voice commands, check out [INSTRUCTIONS.md](./INSTRUCTIONS.md) 📖.

🛠️ Development notes
-----------------

- Entry point: `main_refactored.py` — routes commands to handlers and falls back to `clients/gemini_client.py` when needed.
- Handlers live in `handlers/` and utilities in `utils/`.

📝 Logs
----

Interactions and debug logs are written to the `logs/` directory (e.g., `logs/assistant.jsonl`).

❗ Troubleshooting
---------------

- If voice I/O fails, ensure microphone and speakers are accessible and dependencies are installed.
- If weather lookups fail, verify `OPENWEATHER_API_KEY` is set and valid.
- If LLM responses are missing, set `GEMINI_API_KEY` and/or `GEMINI_API_ENDPOINT`.

➡️ Next steps
----------

- Add `OPENWEATHER_API_KEY` to your `.env` to enable weather features.
- Optionally configure `clients/gemini_client.py` to your LLM provider.

📄 License
-------

This project is licensed under the MIT License — see `LICENSE` for details.
