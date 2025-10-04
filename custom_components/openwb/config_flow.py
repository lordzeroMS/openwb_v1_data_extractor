from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from aiohttp import ClientError

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_PATH, DEFAULT_TIMEOUT, DOMAIN


async def _async_validate_input(hass: HomeAssistant, data: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect to openWB."""

    host_input = data[CONF_HOST].strip()
    if host_input.startswith("http://") or host_input.startswith("https://"):
        base = host_input.rstrip("/")
        url = f"{base}{API_PATH}"
        normalized_host = base
    else:
        normalized_host = host_input.rstrip("/")
        url = f"http://{normalized_host}{API_PATH}"

    session = async_get_clientsession(hass)

    try:
        async with asyncio.timeout(DEFAULT_TIMEOUT):
            async with session.get(url) as response:
                response.raise_for_status()
                payload = await response.json(content_type=None)
    except asyncio.TimeoutError as err:
        raise CannotConnect from err
    except ClientError as err:
        raise CannotConnect from err
    except ValueError as err:
        raise InvalidResponse from err

    if not isinstance(payload, dict):
        raise InvalidResponse

    title = data.get(CONF_NAME) or payload.get("systemName") or f"openWB {normalized_host}"

    return {
        "title": title,
        "host": normalized_host,
        "unique_id": normalized_host,
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for openWB."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await _async_validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidResponse:
                errors["base"] = "invalid_response"
            except Exception:  # pragma: no cover - safety net
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["unique_id"])

                updates: dict[str, Any] = {CONF_HOST: info["host"]}
                if user_input.get(CONF_NAME):
                    updates[CONF_NAME] = user_input[CONF_NAME]

                self._abort_if_unique_id_configured(updates=updates)

                return self.async_create_entry(title=info["title"], data=updates)

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_NAME): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidResponse(HomeAssistantError):
    """Error to indicate the API returned invalid data."""
