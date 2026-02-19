"""Logging utilities"""
import os
import json
import time

def log_interaction(user: str, response: str, source: str = "local"):
    """Append a JSON line with the interaction to logs/assistant.jsonl"""
    try:
        _dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(_dir, exist_ok=True)
        entry = {"ts": time.time(), "user": user, "response": response, "source": source}
        with open(os.path.join(_dir, "assistant.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass
