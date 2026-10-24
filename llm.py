"""Single unified LLM/VLM gateway for SahiCheck.
Calls Gemma 4 via the Gemini API (google-genai SDK) first, and automatically
falls back to local Ollama (Gemma 4 E4B) if offline or rate-limited.
"""

import base64
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemma-4-31b-it").strip()
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").strip().rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e4b").strip()

# Open-weight Gemma candidate tags on the Gemini API
GEMINI_GEMMA_CANDIDATES = [
    GEMINI_MODEL,
    "gemma-4-31b-it",
    "gemma-3-27b-it",
]


def extract_json_object(raw_text: str) -> Dict[str, Any]:
    """Safely extracts the first valid JSON object from model output."""
    if not raw_text:
        raise ValueError("Empty response from model.")

    cleaned = raw_text.strip()
    # Strip markdown code fences if present
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, flags=re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1).strip()

    # Try direct load
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    # Find outermost braces
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = cleaned[start : end + 1]
        data = json.loads(snippet)
        if isinstance(data, dict):
            return data

    raise ValueError("Could not parse valid JSON object from model output.")


def _call_gemini_api(prompt: str, images: Optional[List[bytes]] = None, timeout: float = 25.0) -> Tuple[str, str]:
    """Calls Gemma on the Gemini API using google-genai SDK."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        raise RuntimeError("GEMINI_API_KEY not configured.")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GEMINI_API_KEY)
    contents: List[Any] = []

    if images:
        for img_bytes in images[:2]:  # Cap at 2 pages/images for speed and token budget
            contents.append(
                types.Part.from_bytes(
                    data=img_bytes,
                    mime_type="image/png",
                )
            )
    contents.append(prompt)

    last_err: Optional[Exception] = None
    seen = set()
    for model_name in GEMINI_GEMMA_CANDIDATES:
        if not model_name or model_name in seen:
            continue
        seen.add(model_name)
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=2048,
                ),
            )
            if response and response.text:
                return response.text, f"gemini-api:{model_name}"
        except Exception as exc:
            last_err = exc
            continue

    raise RuntimeError(f"Gemini API call failed: {last_err}")


def _call_ollama(prompt: str, images: Optional[List[bytes]] = None, timeout: float = 35.0) -> Tuple[str, str]:
    """Calls local Ollama with Gemma 4 E4B as offline fallback."""
    payload: Dict[str, Any] = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1,
        },
    }
    if images:
        payload["images"] = [base64.b64encode(img).decode("ascii") for img in images[:2]]

    url = f"{OLLAMA_HOST}/api/generate"
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        body = resp.json()
        text = body.get("response", "")
        if not text:
            raise RuntimeError("Empty response from Ollama.")
        return text, f"ollama:{OLLAMA_MODEL}"


def call_gemma(
    prompt: str,
    images: Optional[List[bytes]] = None,
    expect_json: bool = True,
) -> Tuple[Any, str]:
    """Unified entry point for all SahiCheck agent calls.
    Tries Gemini API (Gemma 4 31B-it) first, then falls back to local Ollama (Gemma 4 E4B).
    Returns (parsed_json_or_text, model_identifier).
    """
    errors: List[str] = []

    # 1. Primary: Gemini API
    try:
        raw_text, model_id = _call_gemini_api(prompt, images=images)
        if expect_json:
            return extract_json_object(raw_text), model_id
        return raw_text, model_id
    except Exception as e:
        errors.append(f"Gemini API: {e}")

    # 2. Fallback: Local Ollama
    try:
        raw_text, model_id = _call_ollama(prompt, images=images)
        if expect_json:
            return extract_json_object(raw_text), model_id
        return raw_text, model_id
    except Exception as e:
        errors.append(f"Ollama fallback: {e}")

    raise RuntimeError("Both Gemini API and Ollama failed: " + " | ".join(errors))