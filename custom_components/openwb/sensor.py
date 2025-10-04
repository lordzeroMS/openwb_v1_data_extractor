from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from importlib import resources
from typing import Any, Callable, Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
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


@dataclass(frozen=True)
class SensorMeta:
    native_unit: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    value_fn: Callable[[Any], StateType] | None = None


@dataclass(frozen=True)
class OpenWBSensorDescription(SensorEntityDescription):
    value_fn: Callable[[Any], StateType] | None = None


LADEMODUS_MAP: dict[int, str] = {
    0: "Sofortladen",
    1: "Min + PV",
    2: "PV-Überschuss",
    3: "Stop",
    4: "Standby",
}


def _parse_timestamp(value: Any) -> StateType:
    if not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value, "%Y:%m:%d-%H:%M:%S")
    except ValueError:
        return None


def _map_lademodus(value: Any) -> StateType:
    try:
        code = int(float(value))
    except (TypeError, ValueError):
        return value

    return LADEMODUS_MAP.get(code, value)


SENSOR_METADATA: dict[str, SensorMeta] = {
    "date": SensorMeta(device_class=SensorDeviceClass.TIMESTAMP, value_fn=_parse_timestamp),
    "lademodus": SensorMeta(value_fn=_map_lademodus),
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
    "llkwhlp1": SensorMeta(
        native_unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "llkwhlp2": SensorMeta(
        native_unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "llkwhlp3": SensorMeta(
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


TRANSLATED_SENSOR_KEYS = _load_translated_sensor_keys()


def _build_descriptions() -> dict[str, OpenWBSensorDescription]:
    descriptions: dict[str, OpenWBSensorDescription] = {}

    for key in TRANSLATED_SENSOR_KEYS:
        meta = SENSOR_METADATA.get(key, SensorMeta())
        descriptions[key] = OpenWBSensorDescription(
            key=key,
            translation_key=key,
            device_class=meta.device_class,
            native_unit_of_measurement=meta.native_unit,
            state_class=meta.state_class,
            value_fn=meta.value_fn,
        )

    return descriptions


SENSOR_DESCRIPTIONS = _build_descriptions()


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
        self._value_fn: Callable[[Any], StateType] | None = None

        lookup_key = key_to_translation_key(key)
        description = SENSOR_DESCRIPTIONS.get(lookup_key)

        if description is not None:
            self.entity_description = description
            self._value_fn = description.value_fn
        else:
            meta = SENSOR_METADATA.get(lookup_key)
            description = OpenWBSensorDescription(
                key=lookup_key,
                name=normalize_key(key),
                device_class=meta.device_class if meta else None,
                native_unit_of_measurement=meta.native_unit if meta else None,
                state_class=meta.state_class if meta else None,
                value_fn=meta.value_fn if meta else None,
            )
            self.entity_description = description
            self._value_fn = description.value_fn
            self._attr_name = description.name

    @property
    def native_value(self) -> StateType:
        """Return the current sensor state."""
        raw = self.coordinator.data.get(self._key)
        if self._value_fn:
            return self._value_fn(raw)
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
