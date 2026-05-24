from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
STRATEGY_FILE = BASE_DIR / "strategies" / "sequence_strategies.json"
DASHBOARD_DIR = BASE_DIR / "dashboard"

API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8090"))

MAX_HISTORY = int(os.getenv("MAX_HISTORY", "200"))
MAX_SIGNALS = int(os.getenv("MAX_SIGNALS", "100"))

AUTO_START_DEMO = os.getenv("AUTO_START_DEMO", "false").lower() == "true"
DEMO_INTERVAL_SECONDS = float(os.getenv("DEMO_INTERVAL_SECONDS", "3.0"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

DEFAULT_GALES = int(os.getenv("DEFAULT_GALES", "2"))
DEFAULT_CONFIDENCE = float(os.getenv("DEFAULT_CONFIDENCE", "0.70"))
ALLOW_WHITE_PROTECTION = os.getenv("ALLOW_WHITE_PROTECTION", "true").lower() == "true"