"""EchoMind AI - Groq Client (Fallback Provider)

This module provides an alternative AI provider using Groq's API. 
In the EchoMind architecture, this client serves as a reliable secondary 
provider that's triggered automatically if the primary Gemini client 
hits rate limits (QuotaExceeded) or encounter errors.

It implements the same interface (`generate_response` and `stream_generate`)
as the Gemini client, making them drop-in replacements for each other.
"""
import os
from typing import Optional, Generator
import requests
import json

# Read config from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_ENDPOINT = os.getenv("GROQ_API_ENDPOINT")
GROQ_RESPONSE_MODE = os.getenv("GROQ_RESPONSE_MODE", "").lower()
# Optional default model to use for OpenAI-compatible Groq endpoints
GROQ_MODEL = os.getenv("GROQ_MODEL", "Ilama-3.1-8b-instant")


def _extract_text_from_data(data):
    # Simple extraction similar to gemini_client._extract_text_from_data
    import json as _json

    if isinstance(data, str):
        s = data.strip()
        if s.startswith("{") or s.startswith("["):
            try:
                parsed = _json.loads(s)
                return _extract_text_from_data(parsed)
            except Exception:
                return s
        return s

    if isinstance(data, dict):
        # try a few common shapes
        for k in ("text", "content", "response", "message"):
            v = data.get(k)
            if isinstance(v, str):
                return v.strip()
        # choices-like
        if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
            c = data["choices"][0]
            if isinstance(c, dict) and "text" in c:
                return c["text"].strip()
        # fallback: find longest string
        longest = None
        def _walk(obj):
            nonlocal longest
            if isinstance(obj, str):
                s = obj.strip()
                if not longest or len(s) > len(longest):
                    longest = s
            elif isinstance(obj, dict):
                for v in obj.values():
                    _walk(v)
            elif isinstance(obj, list):
                for v in obj:
                    _walk(v)
        try:
            _walk(data)
        except Exception:
            pass
        if longest:
            return longest

    return None


def normalize_response(raw):
    if raw is None:
        return ""
    if isinstance(raw, (bytes, bytearray)):
        try:
            raw = raw.decode("utf-8", errors="ignore")
        except Exception:
            raw = str(raw)
    if isinstance(raw, (dict, list)):
        out = _extract_text_from_data(raw)
        return out or ""
    if isinstance(raw, str):
        s = raw.strip()
        # try parse JSON
        if s.startswith("{") or s.startswith("["):
            try:
                import json as _json
                parsed = _json.loads(s)
                out = _extract_text_from_data(parsed)
                if out:
                    return out
            except Exception:
                pass
        return s
    return str(raw)


def call_http_endpoint(prompt: str, timeout: float = 15.0) -> Optional[str]:
    """Call configured Groq HTTP endpoint and return extracted text or raise.

    This helper supports both a full `/responses` URL in `GROQ_API_ENDPOINT`
    or a base OpenAI-compatible URL like `https://api.groq.com/openai/v1`.
    In the latter case it will POST to `<GROQ_API_ENDPOINT>/responses` with
    an OpenAI-compatible payload `{model, input}`.
    """
    if not GROQ_API_ENDPOINT:
        return None
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not set.")

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    # If using the standard OpenAI-compatible completions endpoint
    if "/chat/completions" in GROQ_API_ENDPOINT:
        url = GROQ_API_ENDPOINT
        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }
    # Fallback/Legacy support
    elif GROQ_API_ENDPOINT.rstrip('/').endswith('/responses'):
        url = GROQ_API_ENDPOINT
        payload = {"input": prompt}
    else:
        # Unexpected endpoint format - default to chat completions structure appended
        url = GROQ_API_ENDPOINT.rstrip('/') + '/chat/completions'
        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        status = resp.status_code
        text = resp.text
        # Attempt to parse JSON body when possible
        try:
            data = resp.json()
        except Exception:
            data = None

        # Log non-200 responses for debugging (do not log API keys)
        if status < 200 or status >= 300:
            try:
                import os as _os, datetime as _dt
                _logdir = _os.path.join(_os.getcwd(), "logs")
                _os.makedirs(_logdir, exist_ok=True)
                _entry = {
                    "ts": _dt.datetime.utcnow().isoformat() + "Z",
                    "url": url,
                    "status": status,
                    "response_snippet": (text or "")[:1000]
                }
                with open(_os.path.join(_logdir, "groq_debug.log"), "a", encoding="utf-8") as _f:
                    _f.write(json.dumps(_entry, ensure_ascii=False) + "\n")
            except Exception:
                pass

        # Raise on HTTP errors to let caller decide fallback behaviour
        try:
            resp.raise_for_status()
        except Exception:
            raise

        # Try to extract common response shapes used by Groq / OpenAI-compatible APIs
        if data is not None:
             # 1) Standard OpenAI Chat Completions: choices -> [0] -> message -> content
            if isinstance(data, dict) and 'choices' in data and isinstance(data['choices'], list) and data['choices']:
                choice = data['choices'][0]
                if isinstance(choice, dict):
                    msg = choice.get('message') or {}
                    if isinstance(msg, dict) and 'content' in msg and isinstance(msg['content'], str):
                        return msg['content'].strip()
                    # Fallback for old completions API
                    if 'text' in choice and isinstance(choice['text'], str):
                        return choice['text'].strip()

            # 2) SDK-like: response.output_text
            if isinstance(data, dict) and 'output_text' in data and isinstance(data['output_text'], str):
                return data['output_text'].strip()

            # 3) Other potential formats (Gemini-like output structure?)
            if isinstance(data, dict) and 'output' in data and isinstance(data['output'], list) and data['output']:
                o0 = data['output'][0]
                if isinstance(o0, dict) and 'content' in o0 and isinstance(o0['content'], list) and o0['content']:
                    c0 = o0['content'][0]
                    if isinstance(c0, dict) and 'text' in c0 and isinstance(c0['text'], str):
                        return c0['text'].strip()

        # Fallback: try a permissive extraction
        extracted = _extract_text_from_data(data) if data is not None else None
        if extracted:
            return extracted

        return text
    except Exception as exc:
        # Log exception details (no secrets)
        try:
            import os as _os, datetime as _dt, traceback as _tb
            _logdir = _os.path.join(_os.getcwd(), "logs")
            _os.makedirs(_logdir, exist_ok=True)
            _entry = {
                "ts": _dt.datetime.utcnow().isoformat() + "Z",
                "url": url,
                "error": str(exc),
                "trace": _tb.format_exc().splitlines()[-10:]
            }
            with open(_os.path.join(_logdir, "groq_debug.log"), "a", encoding="utf-8") as _f:
                _f.write(json.dumps(_entry, ensure_ascii=False) + "\n")
        except Exception:
            pass
        raise


def generate_response(prompt: str) -> str:
    """Blocking call returning best-effort text from Groq endpoint."""
    # Optionally wrap prompt to request plain text
    prompt_to_send = prompt
    if GROQ_RESPONSE_MODE == "plain_text":
        prompt_to_send = "Respond only with the final answer in plain text. Do not include JSON, metadata, or code fences.\n\n" + prompt

    if GROQ_API_ENDPOINT:
        try:
            out = call_http_endpoint(prompt_to_send)
            if out is not None:
                return normalize_response(out)
        except Exception:
            pass

    return "I'm having trouble connecting to the groq.ai backend right now."


def stream_generate(prompt: str) -> Generator[str, None, None]:
    """Simple streaming wrapper — Groq fallback yields a single final response."""
    try:
        resp = generate_response(prompt)
        if resp:
            yield resp
            return
    except Exception:
        pass
    yield "I'm having trouble reaching the groq.ai service right now."


__all__ = ["GROQ_API_KEY", "GROQ_API_ENDPOINT", "generate_response", "stream_generate"]
