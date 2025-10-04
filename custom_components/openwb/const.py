from __future__ import annotations

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "openwb"
PLATFORMS: list[Platform] = [Platform.SENSOR]
API_PATH = "/openWB/web/api.php?get=all"
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=30)
DEFAULT_TIMEOUT = 10

# Mapping of raw API keys to Home Assistant translation keys for nicer names.
SENSOR_NAME_MAP: dict[str, str] = {
    "lademodus": "charging_mode",
    "plugstatLP1": "lp1_plug_state",
    "plugstatLP2": "lp2_plug_state",
    "plugstatLP3": "lp3_plug_state",
    "llsoll": "target_charge_power",
    "lllp1": "lp1_charge_power",
    "lllp2": "lp2_charge_power",
    "lllp3": "lp3_charge_power",
    "gelkwhlp1": "lp1_total_energy",
    "gelkwhlp2": "lp2_total_energy",
    "gelkwhlp3": "lp3_total_energy",
    "speichersoc": "battery_soc",
    "speicherpower": "battery_power",
    "hausverbrauch": "house_consumption",
    "evu_w": "grid_power",
    "pvw": "pv_power",
    "charger_soc": "ev_soc",
    "chargestate": "charge_state",
    "ladeleistungaktu": "instant_charge_power",
    "laadetermin": "charge_timer_end",
    "evseconnected": "evse_connected",
    "evseplugged": "evse_plugged",
    "wallboxTemp": "wallbox_temperature",
    "umgebungstemperatur": "ambient_temperature",
    "aussentemperatur": "outside_temperature",
    "lfm_status": "load_management_status",
    "lfm_w": "load_management_power",
    "speichersocziel": "battery_target_soc",
    "socManu": "manual_soc",
    "socCon": "configured_soc",
    "lastmanagementw": "load_management_power_total",
    "phasenzahllp1": "lp1_phase_count",
    "phasenzahllp2": "lp2_phase_count",
    "phasenzahllp3": "lp3_phase_count",
    "phasel1amp": "phase_l1_current",
    "phasel2amp": "phase_l2_current",
    "phasel3amp": "phase_l3_current",
    "llapl1": "lp1_current",
    "llvpl1": "lp1_voltage",
    "llapl2": "lp2_current",
    "llvpl2": "lp2_voltage",
    "llapl3": "lp3_current",
    "llvpl3": "lp3_voltage",
    "lfmampere": "load_management_current",
}

def normalize_key(key: str) -> str:
    """Normalize API keys for entity display."""
    return key.replace("_", " ").replace("-", " ").title()
