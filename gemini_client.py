"""Lightweight Gemini client template.

This module provides a small, safe wrapper for reading the GEMINI_API_KEY from
the environment and shows where to implement real streaming calls to Gemini.

Important: This file does NOT contain any real key and does not make network
calls. Replace the `stream_response_stub` with an actual implementation that
uses your provider's streaming SDK or HTTP/gRPC/WebSocket API.
"""

import os
from typing import Generator, Optional
import requests

# Read config from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Optional: provider-specific HTTP endpoint (leave empty to use local stub)
GEMINI_API_ENDPOINT = os.getenv("GEMINI_API_ENDPOINT")
# Optional: name of header to send the API key in. If not set, Authorization: Bearer <key>
# Example for Google API key header: X-goog-api-key
GEMINI_API_KEY_HEADER = os.getenv("GEMINI_API_KEY_HEADER")
# Optional: control response formatting and prompt wrapping
GEMINI_RESPONSE_MODE = os.getenv("GEMINI_RESPONSE_MODE", "").lower()  # e.g. 'plain_text'
GEMINI_PROMPT_WRAPPER = os.getenv("GEMINI_PROMPT_WRAPPER", "").strip()


def _extract_text_from_data(data):
    """Try to extract a human-readable text reply from a parsed JSON object
    or from a raw text string that may contain JSON. Returns a string or None.
    The function looks for common Gemini/LLM shapes (candidates -> content
    -> parts -> text) and falls back to finding the longest string value in
    the JSON tree.
    """
    import json as _json

    # If it's a string, try to parse JSON out of it first
    if isinstance(data, str):
        s = data.strip()
        # quick heuristic: if it looks like JSON try to parse
        if s.startswith("{") or s.startswith("["):
            try:
                parsed = _json.loads(s)
                return _extract_text_from_data(parsed)
            except Exception:
                # not JSON, return the raw string
                return s
        return s

    # If it's a dict, check common locations
    if isinstance(data, dict):
        # 1) candidates -> [0] -> content -> parts -> [0] -> text
        if "candidates" in data and isinstance(data["candidates"], list) and data["candidates"]:
            cand = data["candidates"][0]
            if isinstance(cand, dict):
                content = cand.get("content")
                if isinstance(content, dict):
                    parts = content.get("parts")
                    if isinstance(parts, list) and parts:
                        first = parts[0]
                        if isinstance(first, dict) and "text" in first and isinstance(first["text"], str):
                            return first["text"].strip()
                # candidate may include 'text' directly
                if "text" in cand and isinstance(cand["text"], str):
                    return cand["text"].strip()

        # 2) output -> [0] -> content -> [0] -> text
        if "output" in data and isinstance(data["output"], list) and data["output"]:
            o0 = data["output"][0]
            if isinstance(o0, dict) and "content" in o0:
                cont = o0.get("content")
                if isinstance(cont, list) and cont:
                    first = cont[0]
                    if isinstance(first, dict) and "text" in first and isinstance(first["text"], str):
                        return first["text"].strip()

        # 3) choices -> [0] -> message -> content
        if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
            choice = data["choices"][0]
            if isinstance(choice, dict):
                msg = choice.get("message") or {}
                if isinstance(msg, dict) and "content" in msg and isinstance(msg["content"], str):
                    return msg["content"].strip()
                if "text" in choice and isinstance(choice["text"], str):
                    return choice["text"].strip()

        # 4) direct keys 'text', 'content', 'response'
        for k in ("text", "content", "response"):
            if k in data and isinstance(data[k], str):
                return data[k].strip()

        # 5) fallback: recursively find the longest string value in the dict
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

    # If nothing found, return None
    return None


def strip_json_noise(text):
    """Ultra-aggressive cleaner: strips JSON keys and metadata entirely.
    Extracts only readable text content from mixed JSON+text responses.
    Removes system prompts and formatting noise.
    """
    import re
    if not isinstance(text, str):
        return str(text)
    
    text = text.strip()
    
    # CRITICAL: Remove system prompt echoes - but be careful not to remove actual content!
    # The system prompt must NEVER reach the user, but we must preserve the answer
    
    # SAFE PATTERN: Only match system prompt at START of response, ending at first newline or period+newline
    # This prevents matching partial sentences from real answers
    system_prompt_start_patterns = [
        # "You are a voice assistant..." - just first sentence
        r"^you are a voice assistant[^.\n]*\.",
        # "Answer the user's question..." - just first sentence  
        r"^answer the user['\']?s question[^.\n]*\.",
        # "Respond only with..." - just first sentence
        r"^respond only with[^.\n]*\.",
        # "I will provide..." - just first sentence
        r"^i will provide[^.\n]*\.",
        # "Okay I understand..." - just that phrase, not everything after
        r"^okay[,.]?\s*(?:i\s+)?understand\.\s*",
    ]
    
    for pattern in system_prompt_start_patterns:
        text = re.sub(pattern, '', text, flags=re.MULTILINE | re.IGNORECASE)
    
    # Now remove JSON metadata keys: "key": value patterns
    # This catches "candidates": [...], "role": "model", etc.
    # But be careful not to remove colons from actual content
    text = re.sub(r'"[^"]*":\s*(?:\{[^}]*\}|\[[^\]]*\]|"[^"]*"|[^,}\]]*)', '', text)
    
    # Remove stray quotes around values
    text = re.sub(r'^"([^"]+)"$', r'\1', text, flags=re.MULTILINE)
    
    # Remove leading/trailing JSON punctuation only
    text = re.sub(r'^[\{\[\,\s]+', '', text)
    text = re.sub(r'[\}\]\,\s]+$', '', text)
    
    # Clean up repeated whitespace but preserve some structure
    text = re.sub(r'[ \t]+', ' ', text)  # Collapse spaces/tabs but keep newlines
    
    # Clean up multiple newlines
    text = re.sub(r'\n\s*\n+', '\n', text)
    
    # Final trim
    text = text.strip()
    
    # If result is empty or just punctuation, return nothing
    if not text or all(not c.isalnum() for c in text):
        return ""
    
    return text


def normalize_response(raw):
    """Public helper: given raw response (str or parsed JSON), return a
    cleaned human-readable string. Safe to call on any API output. Returns
    an empty string when nothing useful is found.
    """
    import json as _json

    if raw is None:
        return ""

    # If it's bytes, decode
    if isinstance(raw, (bytes, bytearray)):
        try:
            raw = raw.decode("utf-8", errors="ignore")
        except Exception:
            raw = str(raw)

    # If it's already a dict/list, extract directly
    if isinstance(raw, (dict, list)):
        out = _extract_text_from_data(raw)
        return out or ""

    # If it's a string, try to parse JSON first
    if isinstance(raw, str):
        s = raw.strip()
        # If it looks like JSON, attempt to parse
        if s.startswith("{") or s.startswith("["):
            try:
                parsed = _json.loads(s)
                out = _extract_text_from_data(parsed)
                if out:
                    return out
            except Exception:
                # Not JSON or parse failed, continue with aggressive strip
                return strip_json_noise(s)

        # Heuristic: remove lines that look like JSON structure or metadata
        lines = [l for l in s.splitlines() if l.strip()]
        cleaned_lines = []
        for line in lines:
            # skip lines that start with JSON structural tokens or keys
            if line.strip().startswith("{") or line.strip().startswith("}"):
                continue
            if any(k in line for k in ["\"candidates\"", "usageMetadata", "modelVersion", "responseId", "avgLogprobs"]):
                continue
            # skip lines that look like JSON arrays/objects
            if line.strip().startswith("[") or line.strip().endswith("]"):
                continue
            cleaned_lines.append(line)

        # join remaining lines; if it's still empty, return original raw trimmed
        joined = "\n".join(cleaned_lines).strip()
        if joined:
            # Final pass through aggressive cleaner
            final = strip_json_noise(joined)
            return final if final else joined

        # Fallback: aggressive strip on original
        return strip_json_noise(s)

    # Last resort
    try:
        return strip_json_noise(str(raw))
    except Exception:
        return ""


def ensure_key():
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set. Put it in .env or environment variables.")


def stream_response_stub(prompt: str) -> Generator[str, None, None]:
    """Stub generator that yields chunks of text like a streaming LLM would.

    Replace this with an implementation that connects to Gemini's streaming
    endpoint and yields tokens/partial text as they arrive.
    """
    sample = (
        "This is a simulated streaming response from Gemini. Replace this stub "
        "with your provider's streaming client to receive real tokens."
    )
    for i in range(0, len(sample), 80):
        yield sample[i : i + 80]


def call_http_endpoint(prompt: str, timeout: float = 15.0) -> Optional[str]:
    """Call a configured HTTP endpoint (if set) and try to extract a text reply.

    The function is intentionally permissive about response shape to support
    different provider formats. It sends a JSON body {"prompt": prompt} and
    supplies the API key as a Bearer token. Set `GEMINI_API_ENDPOINT` in your
    environment to enable this behaviour.
    """
    if not GEMINI_API_ENDPOINT:
        return None
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY must be set to call GEMINI_API_ENDPOINT")

    # Support custom API key header (e.g., X-goog-api-key) or default to
    # Authorization: Bearer <key> when GEMINI_API_KEY_HEADER is not provided.
    if GEMINI_API_KEY_HEADER:
        headers = {GEMINI_API_KEY_HEADER: GEMINI_API_KEY, "Content-Type": "application/json"}
    else:
        headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
    # Optionally wrap the prompt to request plain-text responses
    prompt_to_send = prompt
    if GEMINI_RESPONSE_MODE == "plain_text":
        if GEMINI_PROMPT_WRAPPER:
            prompt_to_send = GEMINI_PROMPT_WRAPPER + "\n\n" + prompt
        else:
            prompt_to_send = "Respond only with the final answer in plain text. Do not include JSON, metadata, or code fences.\n\n" + prompt

    payload = {"prompt": prompt_to_send}
    try:
        resp = requests.post(GEMINI_API_ENDPOINT, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
        # Attempt to parse JSON; if it fails we'll log raw text
        try:
            data = resp.json()
        except Exception:
            data = None
        # Log request/response for debugging (safe: do not log API keys)
        try:
            import json as _json, os as _os, datetime as _dt
            _logdir = _os.path.join(_os.getcwd(), "logs")
            _os.makedirs(_logdir, exist_ok=True)
            _entry = {"ts": _dt.datetime.utcnow().isoformat()+"Z", "endpoint": GEMINI_API_ENDPOINT, "prompt": prompt, "response_text": resp.text}
            with open(_os.path.join(_logdir, "gemini_responses.jsonl"), "a", encoding="utf-8") as _f:
                _f.write(_json.dumps(_entry, ensure_ascii=False)+"\n")
        except Exception:
            pass
        # Try to extract a human-friendly text from the parsed JSON or raw
        # response body. This handles cases where the model returns structured
        # objects or plain text.
        extracted = _extract_text_from_data(data) if data is not None else None
        if extracted:
            return extracted
        # Fallback to raw text if no extraction succeeded
        return resp.text
    except Exception:
        # Bubble up the error to the caller for logging/handling
        raise


def call_google_generate(prompt: str, timeout: float = 15.0, retry_count: int = 3) -> Optional[str]:
    """Call Google Generative Language `generateContent` endpoint.

    Builds the request body matching the curl example and attempts to extract
    a useful text reply from the JSON response. This function does not embed
    any key; it uses GEMINI_API_KEY and GEMINI_API_KEY_HEADER from environment.
    
    Retries on 429 (rate limit) errors with exponential backoff.
    """
    if not GEMINI_API_ENDPOINT:
        return None
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY must be set to call Google endpoint")

    headers = {"Content-Type": "application/json"}
    # Google API requires x-goog-api-key header for API key authentication
    headers["x-goog-api-key"] = GEMINI_API_KEY

    # Google generateContent expects `contents: [{parts: [{text: ...}]}]`
    prompt_to_send = prompt
    if GEMINI_RESPONSE_MODE == "plain_text":
        if GEMINI_PROMPT_WRAPPER:
            prompt_to_send = GEMINI_PROMPT_WRAPPER + "\n\n" + prompt
        else:
            prompt_to_send = "Respond only with the final answer in plain text. Do not include JSON, metadata, or code fences.\n\n" + prompt

    payload = {"contents": [{"parts": [{"text": prompt_to_send}]}]}
    
    import time
    for attempt in range(retry_count):
        try:
            resp = requests.post(GEMINI_API_ENDPOINT, json=payload, headers=headers, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            extracted = _extract_text_from_data(data)
            if extracted:
                return extracted
            return resp.text
        except requests.exceptions.Timeout:
            print(f"WARNING: API timeout calling {GEMINI_API_ENDPOINT} (attempt {attempt+1}/{retry_count})")
            if attempt < retry_count - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                print(f"  Retrying in {wait_time}s...")
                time.sleep(wait_time)
            return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limit - retry with backoff
                print(f"WARNING: API rate limited (429) - (attempt {attempt+1}/{retry_count})")
                if attempt < retry_count - 1:
                    wait_time = 2 ** (attempt + 1)  # More aggressive backoff for rate limits: 2, 4, 8 seconds
                    print(f"  Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    # Last attempt failed, return None
                    return None
            else:
                print(f"WARNING: API HTTP error {resp.status_code}: {e}")
                return None
        except Exception as e:
            print(f"WARNING: API error: {e}")
            return None
    
    return None


__all__ = ["GEMINI_API_KEY", "GEMINI_API_ENDPOINT", "ensure_key", "stream_response_stub", "call_http_endpoint"]


def generate_response(prompt: str) -> str:
    """Convenience blocking helper that returns a full response string.

    Behavior:
    - If GEMINI_API_ENDPOINT is set, call the HTTP endpoint using the API key
      and return the best-effort text extraction from the response.
    - If API fails, return a user-friendly error message instead of stub.
    """
    # Inject current date into prompt for accurate time-based answers
    import datetime
    from datetime import datetime as dt
    now = dt.now()
    current_date = now.strftime("%B %d, %Y")  # e.g., "November 05, 2025"
    current_time = now.strftime("%H:%M:%S")   # e.g., "14:30:45"
    
    # Enhanced prompt with date/time context
    enhanced_prompt = prompt
    if GEMINI_PROMPT_WRAPPER:
        # Replace placeholder dates if they exist, or prepend date info
        wrapper = GEMINI_PROMPT_WRAPPER
        # Add current date/time to wrapper if not already there
        if "current date" not in wrapper.lower():
            wrapper = f"Today's date is {current_date} and the current time is {current_time}. " + wrapper
        enhanced_prompt = wrapper + "\n\n" + prompt
    else:
        enhanced_prompt = f"Today's date is {current_date} and the current time is {current_time}. " + prompt
    
    # If the configured endpoint looks like Google's Generative API or the key
    # header indicates Google, try the Google-specific caller first.
    try_google = False
    if GEMINI_API_ENDPOINT and "generativelanguage.googleapis.com" in GEMINI_API_ENDPOINT:
        try_google = True
    if GEMINI_API_KEY_HEADER and "goog" in GEMINI_API_KEY_HEADER.lower():
        try_google = True

    if try_google and GEMINI_API_ENDPOINT:
        try:
            out = call_google_generate(enhanced_prompt)
            if out is not None:
                return out
        except Exception as e:
            # Don't print - let it continue to fallback
            pass

    # Try generic HTTP endpoint next (real provider)
    if GEMINI_API_ENDPOINT:
        try:
            out = call_http_endpoint(enhanced_prompt)
            if out is not None:
                return out
        except Exception as e:
            # Don't print - let it continue to fallback
            pass

    # If both API calls failed/returned None, return error message instead of stub
    return "I'm having trouble connecting to my AI backend right now. Please try again in a moment."


def stream_generate(prompt: str):
    """Generator that yields incremental text chunks.

    Behavior:
    - If GEMINI_API_STREAM is set (true/1) and GEMINI_API_ENDPOINT is configured,
      attempt a streaming HTTP POST and yield incoming lines/chunks.
    - Otherwise, fall back to the blocking call.
    """
    import re
    import json as _json
    import datetime
    from datetime import datetime as dt
    
    # Inject current date into prompt for accurate time-based answers
    now = dt.now()
    current_date = now.strftime("%B %d, %Y")  # e.g., "November 05, 2025"
    current_time = now.strftime("%H:%M:%S")   # e.g., "14:30:45"
    
    # Enhanced prompt with date/time context
    enhanced_prompt = prompt
    if GEMINI_PROMPT_WRAPPER:
        wrapper = GEMINI_PROMPT_WRAPPER
        # Add current date/time to wrapper if not already there
        if "current date" not in wrapper.lower():
            wrapper = f"Today's date is {current_date} and the current time is {current_time}. " + wrapper
        enhanced_prompt = wrapper + "\n\n" + prompt
    else:
        enhanced_prompt = f"Today's date is {current_date} and the current time is {current_time}. " + prompt
    
    stream_flag = os.getenv("GEMINI_API_STREAM", "").lower() in ("1", "true", "yes")
    
    if stream_flag and GEMINI_API_ENDPOINT and GEMINI_API_KEY:
        # Check if it's a Google endpoint
        is_google = "generativelanguage.googleapis.com" in GEMINI_API_ENDPOINT
        
        headers = {"Content-Type": "application/json"}
        # Google API requires x-goog-api-key header for API key authentication
        if is_google:
            headers["x-goog-api-key"] = GEMINI_API_KEY
        else:
            headers["Authorization"] = f"Bearer {GEMINI_API_KEY}"
        
        # Use proper payload format for Google API
        prompt_to_send = enhanced_prompt
        if GEMINI_RESPONSE_MODE == "plain_text":
            if GEMINI_PROMPT_WRAPPER:
                prompt_to_send = GEMINI_PROMPT_WRAPPER + "\n\n" + enhanced_prompt
            else:
                prompt_to_send = "Respond only with the final answer in plain text. Do not include JSON, metadata, or code fences.\n\n" + enhanced_prompt

        if is_google:
            payload = {"contents": [{"parts": [{"text": prompt_to_send}]}]}
        else:
            payload = {"prompt": prompt_to_send}
        
        stream_success = False
        try:
            with requests.post(GEMINI_API_ENDPOINT, json=payload, headers=headers, stream=True, timeout=30) as resp:
                resp.raise_for_status()
                
                chunk_count = 0
                for raw in resp.iter_lines(decode_unicode=True):
                    if not raw:
                        continue
                    
                    # IMPROVED: Extract "text": "..." by finding the field and then JSON-parsing it
                    # Look for "text": followed by a colon and potential whitespace, then capture until end of field
                    text_match = re.search(r'"text"\s*:\s*', raw)
                    if text_match:
                        # Start position after "text":
                        start_pos = text_match.end()
                        # Try to extract the JSON string value starting at this position
                        try:
                            # Use json.JSONDecoder to properly parse the string value
                            decoder = _json.JSONDecoder()
                            text_content, _ = decoder.raw_decode(raw[start_pos:])
                            
                            # text_content is now the properly unescaped string
                            if text_content and isinstance(text_content, str):
                                if text_content.strip():  # Only if non-empty
                                    cleaned = strip_json_noise(text_content)
                                    if cleaned and any(ch.isalnum() for ch in cleaned):
                                        yield cleaned
                                        chunk_count += 1
                                        stream_success = True
                            continue
                        except Exception as e:
                            # Fall through to try other parsing methods
                            pass
                    
                    # Try parsing entire line as complete JSON
                    try:
                        part = _json.loads(raw)
                        extracted = _extract_text_from_data(part)
                        if extracted:
                            cleaned = strip_json_noise(extracted)
                            if cleaned and any(ch.isalnum() for ch in cleaned):
                                yield cleaned
                                chunk_count += 1
                                stream_success = True
                        continue
                    except Exception:
                        pass  # Not valid JSON, skip
                
                if stream_success:
                    return  # Successfully streamed
        except requests.exceptions.HTTPError as e:
            print(f"WARNING: Streaming HTTP error {e.response.status_code}: {e}")
        except Exception as e:
            print(f"WARNING: Streaming failed: {e}")

    # Fallback: use blocking call instead
    try:
        response = generate_response(prompt)
        if response:
            yield response
            return
    except Exception as e:
        print(f"WARNING: Fallback generate_response failed: {e}")
    
    # Last resort: inform user of API issue
    yield "I'm having trouble reaching the AI service right now. Please try again in a moment."

