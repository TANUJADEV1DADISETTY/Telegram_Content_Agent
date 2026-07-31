import os
import logging

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("telegram-content-agent")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GOOGLE_SHEETS_CREDENTIALS_JSON = os.environ.get("GOOGLE_SHEETS_CREDENTIALS_JSON")
GOOGLE_SHEET_NAME = os.environ.get("GOOGLE_SHEET_NAME", "Telegram Content Agent")
GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")

DB_PATH = os.environ.get("DB_PATH", "data/agent.db")

def validate_config():
    errors = []
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN is missing")
    if not GOOGLE_SHEETS_CREDENTIALS_JSON:
        errors.append("GOOGLE_SHEETS_CREDENTIALS_JSON is missing")
        
    if LLM_PROVIDER not in ["ollama", "gemini", "groq"]:
        errors.append(f"LLM_PROVIDER must be one of: 'ollama', 'gemini', 'groq'. Got '{LLM_PROVIDER}'")
        
    if LLM_PROVIDER == "gemini" and not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY is required when LLM_PROVIDER='gemini'")
    if LLM_PROVIDER == "groq" and not GROQ_API_KEY:
        errors.append("GROQ_API_KEY is required when LLM_PROVIDER='groq'")
        
    if errors:
        raise ValueError("Configuration validation failed:\n" + "\n".join(errors))
        
    logger.info(f"Configuration loaded. Provider: {LLM_PROVIDER}. DB Path: {DB_PATH}")
