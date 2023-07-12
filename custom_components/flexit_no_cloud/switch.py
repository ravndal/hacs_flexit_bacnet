"""The Flexit Nordic (BACnet) integration."""
import asyncio.exceptions

from flexit_bacnet import FlexitBACnet
from flexit_bacnet.bacnet import DecodingError

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the Flexit Nordic unit."""
    device = hass.data[DOMAIN][config_entry.entry_id]

    async_add_devices(
        [FlexitComfortButtonSwitch(device), FlexitCookerHoodSwitch(device)]
    )


class FlexitComfortButtonSwitch(SwitchEntity):
    """Flexit comfort button."""

    def __init__(self, device: FlexitBACnet) -> None:
        """Initialize the switch."""
        self._device = device
        self._attr_unique_id = f"{device.serial_number}_comfort_button"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (DOMAIN, device.serial_number),
            },
            name="Comfort Button",
            manufacturer="Flexit",
            model="Nordic",
        )

    async def async_update(self) -> None:
        """Refresh unit state."""
        await self._device.update()

    @property
    def is_on(self) -> bool:
        """Return true if the comfort button is on."""
        return self._device.comfort_button

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the comfort button on."""
        try:
            await self._device.activate_comfort_button()
        except (asyncio.exceptions.TimeoutError, ConnectionError, DecodingError) as exc:
            raise HomeAssistantError from exc

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the comfort button off."""
        try:
            await self._device.deactivate_comfort_button()
        except (asyncio.exceptions.TimeoutError, ConnectionError, DecodingError) as exc:
            raise HomeAssistantError from exc


class FlexitCookerHoodSwitch(SwitchEntity):
    """Flexit cooker hood."""

    def __init__(self, device: FlexitBACnet) -> None:
        """Initialize the switch."""
        self._device = device
        self._attr_unique_id = f"{device.serial_number}_cooker_hood"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (DOMAIN, device.serial_number),
            },
            name="Cooker Hood",
            manufacturer="Flexit",
            model="Nordic",
        )

    async def async_update(self) -> None:
        """Refresh unit state."""
        await self._device.update()

    @property
    def is_on(self) -> bool:
        """Return true if the cooker hood is on."""
        return self._device.cooker_hood

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the cooker hood on."""
        try:
            await self._device.activate_cooker_hood()
        except (asyncio.exceptions.TimeoutError, ConnectionError, DecodingError) as exc:
            raise HomeAssistantError from exc

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the cooker hood off."""
        try:
            await self._device.deactivate_cooker_hood()
        except (asyncio.exceptions.TimeoutError, ConnectionError, DecodingError) as exc:
            raise HomeAssistantError from exc
