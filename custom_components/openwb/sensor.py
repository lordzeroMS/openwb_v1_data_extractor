from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from importlib import resources
from typing import Any, Callable, Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import StateType

from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)

from .const import DOMAIN, key_to_translation_key, normalize_key
from .coordinator import OpenWBDataUpdateCoordinator


def _load_translated_sensor_keys() -> set[str]:
    try:
        with resources.files(__package__).joinpath("strings.json").open(encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):  # pragma: no cover - defensive
        return set()

    sensors = data.get("entity", {}).get("sensor", {})
    return {key.lower() for key in sensors}


TRANSLATED_SENSOR_KEYS = _load_translated_sensor_keys()


@dataclass(frozen=True)
class SensorMeta:
    native_unit: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    value_fn: Callable[[Any], StateType] | None = None


def _parse_timestamp(value: Any) -> StateType:
    if not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value, "%Y:%m:%d-%H:%M:%S")
    except ValueError:
        return None


SENSOR_METADATA: dict[str, SensorMeta] = {
    "date": SensorMeta(device_class=SensorDeviceClass.TIMESTAMP, value_fn=_parse_timestamp),
    "lademodus": SensorMeta(),
    "minimalstromstaerke": SensorMeta(
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "maximalstromstaerke": SensorMeta(
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "llsoll": SensorMeta(
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "gelkwhlp1": SensorMeta(
        native_unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    "gelkwhlp2": SensorMeta(
        native_unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    "gelkwhlp3": SensorMeta(
        native_unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    "gelrlp1": SensorMeta(
        native_unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "gelrlp2": SensorMeta(
        native_unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "gelrlp3": SensorMeta(
        native_unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "llgesamt": SensorMeta(
        native_unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "evua1": SensorMeta(
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "evua2": SensorMeta(
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "evua3": SensorMeta(
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "lllp1": SensorMeta(
        native_unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "lllp2": SensorMeta(
        native_unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "lllp3": SensorMeta(
        native_unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "evuw": SensorMeta(
        native_unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "pvw": SensorMeta(
        native_unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "evuv1": SensorMeta(
        native_unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "evuv2": SensorMeta(
        native_unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "evuv3": SensorMeta(
        native_unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "speichersoc": SensorMeta(
        native_unit=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "soclp1": SensorMeta(
        native_unit=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "soclp2": SensorMeta(
        native_unit=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "speichersocziel": SensorMeta(
        native_unit=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "speicherleistung": SensorMeta(
        native_unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "speicherpower": SensorMeta(
        native_unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "hausverbrauch": SensorMeta(
        native_unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "pvwh": SensorMeta(
        native_unit=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "evubezugwh": SensorMeta(
        native_unit=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "evueinspeisungwh": SensorMeta(
        native_unit=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "wallboxtemp": SensorMeta(
        native_unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "umgebungstemperatur": SensorMeta(
        native_unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "aussentemperatur": SensorMeta(
        native_unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "lla1lp1": SensorMeta(
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "lla2lp1": SensorMeta(
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "lla3lp1": SensorMeta(
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "lla1lp2": SensorMeta(
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "lla2lp2": SensorMeta(
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "lla3lp2": SensorMeta(
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "lla1lp3": SensorMeta(
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "lla2lp3": SensorMeta(
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "lla3lp3": SensorMeta(
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "llvpl1": SensorMeta(
        native_unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "llvpl2": SensorMeta(
        native_unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "llvpl3": SensorMeta(
        native_unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "llapl1": SensorMeta(
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "llapl2": SensorMeta(
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "llapl3": SensorMeta(
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "restzeitlp1m": SensorMeta(
        native_unit=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "restzeitlp2m": SensorMeta(
        native_unit=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "restzeitlp3m": SensorMeta(
        native_unit=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
    ),
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up openWB sensors based on a config entry."""

    coordinator: OpenWBDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    created_keys: set[str] = set()

    async def _async_discover_entities() -> None:
        new_entities: list[OpenWBSensor] = []
        for key in sorted(coordinator.data):
            if key in created_keys:
                continue
            created_keys.add(key)
            new_entities.append(OpenWBSensor(coordinator, entry, key))

        if new_entities:
            async_add_entities(new_entities)

    await _async_discover_entities()

    def _handle_coordinator_update() -> None:
        hass.async_create_task(_async_discover_entities())

    unregister = coordinator.async_add_listener(_handle_coordinator_update)
    entry.async_on_unload(unregister)


class OpenWBSensor(CoordinatorEntity[OpenWBDataUpdateCoordinator], SensorEntity):
    """Representation of a single openWB sensor value."""

    _attr_has_entity_name: Final[bool] = True

    def __init__(
        self,
        coordinator: OpenWBDataUpdateCoordinator,
        entry: ConfigEntry,
        key: str,
    ) -> None:
        super().__init__(coordinator)
        self._key = key
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}-{key}"

        translation_key = key_to_translation_key(key)
        self._translation_key = translation_key
        meta = SENSOR_METADATA.get(translation_key)
        self._meta = meta

        if translation_key in TRANSLATED_SENSOR_KEYS:
            self._attr_translation_key = translation_key
            self._attr_name = None
        else:
            self._attr_name = normalize_key(key)

        if meta is not None:
            self._attr_native_unit_of_measurement = meta.native_unit
            self._attr_device_class = meta.device_class
            self._attr_state_class = meta.state_class

    @property
    def native_value(self) -> StateType:
        """Return the current sensor state."""
        raw = self.coordinator.data.get(self._key)
        if self._meta and self._meta.value_fn:
            return self._meta.value_fn(raw)
        return _coerce_value(raw)

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information for the openWB hub."""
        host = self.coordinator.host
        if host.startswith("http://") or host.startswith("https://"):
            configuration_url = host
        else:
            configuration_url = f"http://{host}"

        return {
            "identifiers": {(DOMAIN, host)},
            "name": self.coordinator.device_name,
            "manufacturer": "openWB",
            "configuration_url": configuration_url,
        }

    @property
    def available(self) -> bool:
        """State availability."""
        return self.coordinator.last_update_success


def _coerce_value(value: Any) -> StateType:
    """Return a Home Assistant compatible state type."""
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return value

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        stripped = value.strip()
        if stripped in {"", "--"}:
            return None
        if stripped.lower() in {"true", "false"}:
            return stripped.lower() == "true"
        try:
            if "." in stripped:
                return float(stripped)
            return int(stripped)
        except ValueError:
            return value

    if isinstance(value, (dict, list)):
        return str(value)

    return str(value)
