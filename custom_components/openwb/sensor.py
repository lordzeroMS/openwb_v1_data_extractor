from __future__ import annotations

from typing import Any, Final

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import StateType

from .const import DOMAIN, SENSOR_NAME_MAP, normalize_key
from .coordinator import OpenWBDataUpdateCoordinator


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

        translation_key = SENSOR_NAME_MAP.get(key)
        if translation_key is not None:
            self._attr_translation_key = translation_key
        else:
            self._attr_name = normalize_key(key)

    @property
    def native_value(self) -> StateType:
        """Return the current sensor state."""
        raw = self.coordinator.data.get(self._key)
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
