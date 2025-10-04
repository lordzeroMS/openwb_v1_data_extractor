from __future__ import annotations

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "openwb"
PLATFORMS: list[Platform] = [Platform.SENSOR]
API_PATH = "/openWB/web/api.php?get=all"
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=30)
DEFAULT_TIMEOUT = 10

def normalize_key(key: str) -> str:
    """Normalize API keys for entity display."""
    return key.replace("_", " ").replace("-", " ").title()
