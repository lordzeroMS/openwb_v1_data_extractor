from __future__ import annotations

from datetime import timedelta
import re

from homeassistant.const import Platform

DOMAIN = "openwb"
PLATFORMS: list[Platform] = [Platform.SENSOR]
API_PATH = "/openWB/web/api.php?get=all"
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=30)
DEFAULT_TIMEOUT = 10


def normalize_key(key: str) -> str:
    """Normalize API keys for entity display."""
    return key.replace("_", " ").replace("-", " ").title()


def key_to_translation_key(key: str) -> str:
    """Create a Home Assistant translation key from an API key."""
    return re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")
