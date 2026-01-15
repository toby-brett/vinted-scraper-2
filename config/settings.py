from pathlib import Path

from config.paths import resolve_under_state, resolve_under_models

ROOT_DATA = Path(resolve_under_state("data"))
ROOT_ID = Path(resolve_under_state("ids"))
ROOT_MODELS = Path(resolve_under_state("models"))
ROOT_JOBS = Path(resolve_under_state("jobs"))
ROOT_LOGS = Path(resolve_under_state("logs"))

# telegram
BOT_TOKEN = "7883319571:AAFmWkHKXKt6UkYlUqT6DSrNsXy2gk0jhzg"
CHAT_ID = "8500213100"

# evaluation
EXPENSES = 2.9 + 0.9

# scraping
INTERVAL = 120
MAX_RETRIES = 3
RETRY_SLEEP_SECONDS = 60
PAGE_RESET_TRY = 2
SCRAPES_TILL_RESET = 10
MAX_ERRORS = 3
BLOCK_COOLDOWN_SECONDS = 60 * 60 * 3
BLOCKED_EXIT_CODE = 67
TIMEOUT_EXIT_CODE = 69

CONDITION_DICT = {
    'new with tags': 4,
    'new without tags': 3,
    'very good': 2,
    'good': 1,
    'satisfactory': 0
}