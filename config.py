import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if present
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

APP_NAME = "GymFlow v3"

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700

SIDEBAR_WIDTH = 240

PRIMARY_COLOR = "#FFC107"
BACKGROUND_COLOR = "#0D1117"
SIDEBAR_COLOR = "#161B22"
CARD_COLOR = "#21262D"

TEXT_COLOR = "#FFFFFF"
SECONDARY_TEXT = "#9CA3AF"

APP_VERSION = "3.0.0"
AUTHOR = "Ibrahim Khalil"
AUTOHR = AUTHOR  # Maintained for backward compatibility
CURRENT_YEAR = "2026"

# Sidebar Button
BUTTON_HEIGHT = 40
BUTTON_RADIUS = 10

BUTTON_PADDING_X = 10
BUTTON_PADDING_Y = 5

BUTTON_HOVER_COLOR = "#242B36"
BUTTON_ACTIVE_COLOR = "#1F2937"

ACTIVE_INDICATOR_COLOR = PRIMARY_COLOR

# Database Configuration (loaded securely via environment variables)
DB_TYPE = os.getenv("DB_TYPE", "mysql").lower()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "gym_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "gym_password")
DB_NAME = os.getenv("DB_NAME", "gym_flow")
SQLITE_FALLBACK = os.getenv("SQLITE_FALLBACK", "true").lower() in ("true", "1", "yes")
SQLITE_PATH = os.getenv("SQLITE_PATH", str(BASE_DIR / "gym.db"))
