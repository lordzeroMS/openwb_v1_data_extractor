from __future__ import annotations

import asyncio
import logging
from typing import Any

from aiohttp import ClientError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_PATH, DEFAULT_TIMEOUT, DEFAULT_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class OpenWBDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to retrieve data from openWB."""

    def __init__(self, hass: HomeAssistant, host: str, name: str) -> None:
        self._host = host.rstrip("/")
        self._session = async_get_clientsession(hass)
        self._name = name

        super().__init__(
            hass,
            _LOGGER,
            name=f"openWB ({self._host})",
            update_interval=DEFAULT_UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        url = f"http://{self._host}{API_PATH}" if not self._host.startswith("http") else f"{self._host.rstrip('/')}{API_PATH}"

        try:
            async with asyncio.timeout(DEFAULT_TIMEOUT):
                async with self._session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json(content_type=None)
        except asyncio.TimeoutError as err:
            raise UpdateFailed("Timeout while communicating with openWB") from err
        except ClientError as err:
            raise UpdateFailed(f"Connection error: {err}") from err
        except ValueError as err:
            raise UpdateFailed(f"Invalid response: {err}") from err

        if not isinstance(data, dict):
            raise UpdateFailed("Unexpected payload structure from openWB API")

        return data

    @property
    def host(self) -> str:
        """Return the configured host."""
        return self._host

    @property
    def device_name(self) -> str:
        """Return a user friendly device name."""
        return self._name or f"openWB {self._host}"

