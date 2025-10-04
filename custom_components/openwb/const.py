from __future__ import annotations

from datetime import timedelta
import re

from homeassistant.const import Platform

DOMAIN = "openwb"
PLATFORMS: list[Platform] = [Platform.SENSOR]
API_PATH = "/openWB/web/api.php?get=all"
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=30)
DEFAULT_TIMEOUT = 10

# Keys that have dedicated translations in strings.json/translations.
TRANSLATED_SENSOR_KEYS: set[str] = {
    "aussentemperatur",
    "charger_soc",
    "chargestate",
    "chargestatlp1",
    "chargestatlp2",
    "chargestatlp3",
    "date",
    "evseconnected",
    "evseplugged",
    "evua1",
    "evua2",
    "evua3",
    "evubezugwh",
    "evueinspeisungwh",
    "evuv1",
    "evuv2",
    "evuv3",
    "evuw",
    "gelkwhlp1",
    "gelkwhlp2",
    "gelkwhlp3",
    "gelrlp1",
    "gelrlp2",
    "gelrlp3",
    "hausverbrauch",
    "lademodus",
    "ladeleistungaktu",
    "ladestartzeitlp1",
    "ladestartzeitlp2",
    "ladestartzeitlp3",
    "ladestatuslp1",
    "ladestatuslp2",
    "ladestatuslp3",
    "ladungaktivlp1",
    "ladungaktivlp2",
    "ladungaktivlp3",
    "laadetermin",
    "lla1lp1",
    "lla1lp2",
    "lla1lp3",
    "lla2lp1",
    "lla2lp2",
    "lla2lp3",
    "lla3lp1",
    "lla3lp2",
    "lla3lp3",
    "llapl1",
    "llapl2",
    "llapl3",
    "llgesamt",
    "llkwhlp1",
    "llkwhlp2",
    "llkwhlp3",
    "lllp1",
    "lllp2",
    "lllp3",
    "llsoll",
    "llvpl1",
    "llvpl2",
    "llvpl3",
    "maximalstromstaerke",
    "minimalstromstaerke",
    "phasel1amp",
    "phasel2amp",
    "phasel3amp",
    "phasenzahllp1",
    "phasenzahllp2",
    "phasenzahllp3",
    "plugstatlp1",
    "plugstatlp2",
    "plugstatlp3",
    "pvw",
    "pvwh",
    "restzeitlp1",
    "restzeitlp1m",
    "restzeitlp2",
    "restzeitlp2m",
    "restzeitlp3",
    "restzeitlp3m",
    "soccon",
    "soclp1",
    "soclp2",
    "socmanu",
    "speicherleistung",
    "speicherpower",
    "speichersoc",
    "speichersocziel",
    "umgebungstemperatur",
    "wallboxtemp",
    "zielladungaktiv",
}


def normalize_key(key: str) -> str:
    """Normalize API keys for entity display."""
    return key.replace("_", " ").replace("-", " ").title()


def key_to_translation_key(key: str) -> str:
    """Create a Home Assistant translation key from an API key."""
    return re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")
