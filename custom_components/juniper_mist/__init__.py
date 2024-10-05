import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import JuniperMistDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Juniper Mist from a config entry."""
    _LOGGER.info("Setting up Juniper Mist integration for entry: %s", entry.entry_id)

    try:
        coordinator = JuniperMistDataUpdateCoordinator(hass, entry)
        await coordinator.async_config_entry_first_refresh()

        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = coordinator

        # Forward the setup to the device_tracker platform
        await hass.config_entries.async_forward_entry_setups(entry, ["device_tracker"])

        _LOGGER.info("Successfully set up Juniper Mist for entry: %s", entry.entry_id)
        return True

    except Exception as ex:
        _LOGGER.error("Error setting up Juniper Mist for entry %s: %s", entry.entry_id, ex)
        return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.info("Unloading Juniper Mist integration for entry: %s", entry.entry_id)

    try:
        unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "device_tracker")
        if unload_ok:
            coordinator = hass.data[DOMAIN].pop(entry.entry_id)
            await coordinator.async_cleanup()

            _LOGGER.info("Successfully unloaded Juniper Mist for entry: %s", entry.entry_id)
            return True
        else:
            _LOGGER.error("Failed to unload Juniper Mist for entry: %s", entry.entry_id)
            return False

    except Exception as ex:
        _LOGGER.error("Error unloading Juniper Mist for entry %s: %s", entry.entry_id, ex)
        return False
