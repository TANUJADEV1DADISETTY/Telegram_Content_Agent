import json
import time
import requests
import google.generativeai as genai

from src.config import (
    LLM_PROVIDER, GEMINI_API_KEY, GROQ_API_KEY,
    OLLAMA_BASE_URL, OLLAMA_MODEL, logger,
)

# ── System prompt shared by all providers ────────────────────────────────────
SYSTEM_PROMPT = """You are an expert content strategist and professional social media copywriter.
Your task is to analyse the provided content and generate a structured JSON object.

You MUST return a single, raw JSON object — no markdown fences, no pre-text, no post-text.

Required schema:
{
  "title": "A concise, compelling title for the content",
  "rationale": "A one-sentence explanation of why this content is valuable or shareable",
  "category": "A single relevant category tag (e.g. 'AI', 'Startups', 'Productivity')",
  "variants": {
    "x_post": "A short, punchy draft for X (Twitter). MUST be ≤ 280 characters.",
    "linkedin_post": "A more professional, longer-form draft for LinkedIn with bullet points."
  }
}

STRICT RULES:
1. Output raw JSON only — no code blocks, no extra keys.
2. 'x_post' MUST be ≤ 280 characters (count carefully).
3. 'x_post' and 'linkedin_post' MUST be distinct texts.
4. 'linkedin_post' should be substantially longer and professional in tone.
"""

CORRECTION_TEMPLATE = (
    "Your previous response was invalid. Error: {error}\n\n"
    "Return ONLY a raw JSON object matching this exact schema — no markdown fences:\n"
    '{{"title":"...","rationale":"...","category":"...",'
    '"variants":{{"x_post":"... ≤280 chars ...","linkedin_post":"..."}}}}'
)


# ── Validation ────────────────────────────────────────────────────────────────
def _validate(data) -> None:
    if not isinstance(data, dict):
        raise ValueError("Root output must be a JSON object.")
    for key in ("title", "rationale", "category", "variants"):
        if key not in data:
            raise ValueError(f"Missing required key: '{key}'")
    variants = data["variants"]
    if not isinstance(variants, dict):
        raise ValueError("'variants' must be a JSON object.")
    for key in ("x_post", "linkedin_post"):
        if key not in variants:
            raise ValueError(f"Missing variant key: '{key}'")
    x = variants["x_post"]
    if not isinstance(x, str):
        raise ValueError("'x_post' must be a string.")
    if len(x) > 280:
        raise ValueError(
            f"'x_post' is {len(x)} characters — exceeds the 280-character limit."
        )
    if not isinstance(variants["linkedin_post"], str):
        raise ValueError("'linkedin_post' must be a string.")


def _strip_fences(text: str) -> str:
    """Remove optional ```json ... ``` wrappers that some models add."""
    text = text.strip()
    for prefix in ("```json", "```"):
        if text.startswith(prefix):
            text = text[len(prefix):]
            break
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


# ── Provider calls ────────────────────────────────────────────────────────────
def _call_ollama(system: str, user: str) -> str:
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"{system}\n\n{user}",
        "format": "json",
        "stream": False,
    }
    logger.info(f"Calling Ollama model '{OLLAMA_MODEL}' at {url}")
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json().get("response", "")


def _call_gemini(system: str, user: str) -> str:
    logger.info("Calling Gemini API (gemini-1.5-flash)")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={"response_mime_type": "application/json"},
        system_instruction=system,
    )
    resp = model.generate_content(user)
    return resp.text


def _call_groq(system: str, user: str) -> str:
    logger.info("Calling Groq API (llama-3.1-8b-instant)")
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.4,
    }
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json=payload, headers=headers, timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _dispatch(system: str, user: str) -> str:
    if LLM_PROVIDER == "gemini":
        return _call_gemini(system, user)
    elif LLM_PROVIDER == "groq":
        return _call_groq(system, user)
    else:
        return _call_ollama(system, user)


# ── Public interface ──────────────────────────────────────────────────────────
def generate_drafts(content: str, style_prompt: str = "") -> dict:
    """Generate structured social-media drafts for *content*.

    Raises ValueError after exhausting retries.
    """
    # Build the user-facing prompt (system_prompt stays separate for providers
    # that support it natively; for Ollama it is prepended inside _call_ollama).
    style_section = (
        f"\nSTYLE INSTRUCTION:\nApply this style to all generated text: '{style_prompt}'\n"
        if style_prompt
        else ""
    )
    user_prompt = f"{style_section}\nCONTENT TO PROCESS:\n{content}"

    retries = 3
    delay = 2
    last_error: Exception | None = None

    for attempt in range(retries):
        try:
            raw = _dispatch(SYSTEM_PROMPT, user_prompt)
            parsed = json.loads(_strip_fences(raw))
            _validate(parsed)
            return parsed

        except Exception as exc:
            last_error = exc
            logger.warning(f"LLM attempt {attempt + 1}/{retries} failed: {exc}")

            if attempt < retries - 1:
                correction = CORRECTION_TEMPLATE.format(error=str(exc))
                user_prompt = f"{user_prompt}\n\n{correction}"
                time.sleep(delay)
                delay *= 2

    raise ValueError(
        f"Failed to produce valid JSON after {retries} attempts. "
        f"Last error: {last_error}"
    )
