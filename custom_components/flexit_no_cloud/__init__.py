"""The Flexit Nordic (BACnet) integration."""
import asyncio.exceptions

from flexit_bacnet import FlexitBACnet
from flexit_bacnet.bacnet import DecodingError

from homeassistant.components.climate import (
    async_setup_entry as async_setup_climate_entry,
)
from homeassistant.components.switch import (
    async_setup_entry as async_setup_switch_entry,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID, CONF_DEVICE, CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers import entity, service
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import HomeAssistantType

from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

CONFIG_SCHEMA = cv.config_entry_only_config_schema

PLATFORMS = ["climate", "switch"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Flexit Nordic component."""
    hass.data[DOMAIN] = {}

    def start_rapid_ventilation(call: ServiceCall) -> None:
        """Start rapid ventilation."""
        entity_id = call.data[ATTR_ENTITY_ID]
        duration = call.data["duration"]

        entity = entity.get_entity_registry(hass).async_get(entity_id)
        if entity is None:
            raise HomeAssistantError(f"No entity with ID {entity_id} found")

        device = hass.data[DOMAIN][entity.config_entry_id]
        device.start_rapid_ventilation(duration)

    def start_fireplace_ventilation(call: ServiceCall) -> None:
        """Start fireplace ventilation."""
        entity_id = call.data[ATTR_ENTITY_ID]
        duration = call.data["duration"]

        entity = entity.get_entity_registry(hass).async_get(entity_id)
        if entity is None:
            raise HomeAssistantError(f"No entity with ID {entity_id} found")

        device = hass.data[DOMAIN][entity.config_entry_id]
        device.start_fireplace_ventilation(duration)

    def reset_air_filter_timer(call: ServiceCall) -> None:
        """Reset the air filter timer."""
        entity_id = call.data[ATTR_ENTITY_ID]

        entity = entity.get_entity_registry(hass).async_get(entity_id)
        if entity is None:
            raise HomeAssistantError(f"No entity with ID {entity_id} found")

        device = hass.data[DOMAIN][entity.config_entry_id]
        device.reset_air_filter_timer()

    hass.services.async_register(
        DOMAIN,
        "start_rapid_ventilation",
        start_rapid_ventilation,
        service.SCHEMA.extend(
            {
                service.ATTR_ENTITY_ID: service.entity_id,
                "duration": int,
            }
        ),
    )

    hass.services.async_register(
        DOMAIN,
        "start_fireplace_ventilation",
        start_fireplace_ventilation,
        service.SCHEMA.extend(
            {
                service.ATTR_ENTITY_ID: service.entity_id,
                "duration": int,
            }
        ),
    )

    hass.services.async_register(
        DOMAIN,
        "reset_air_filter_timer",
        reset_air_filter_timer,
        service.SCHEMA.extend(
            {
                service.ATTR_ENTITY_ID: service.entity_id,
            }
        ),
    )

    return True


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry) -> bool:
    """Set up a Flexit device from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    device_id = entry.data[CONF_DEVICE]

    try:
        device = await FlexitBACnet.connect(host, port, device_id)
    except (asyncio.exceptions.TimeoutError, ConnectionError, DecodingError):
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = device

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def async_unload_entry(hass: HomeAssistantType, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
