
import logging
from datetime import timedelta
import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, CONF_SITE_ID, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

class JuniperMistDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch data from Juniper Mist API."""

    def __init__(self, hass, config_entry):
        """Initialize the coordinator."""
        self.site_id = config_entry.data[CONF_SITE_ID]
        self.api_key = config_entry.data[CONF_API_KEY]
        self.session = aiohttp.ClientSession()
        self.known_devices = {}  # Keep track of known devices

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=300),  # 5 minutes
        )

    async def _async_update_data(self):
        """Fetch data from Juniper Mist API."""
        url = f"https://api.eu.mist.com/api/v1/sites/{self.site_id}/stats/clients?limit=500"
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status != 200:
                    text = await response.text()
                    raise UpdateFailed(f"API returned status {response.status}: {text}")
                data = await response.json()

                # Update known devices, keep the MAC as the key
                updated_devices = {client["mac"]: client for client in data if isinstance(client, dict)}

                # Set previously known devices to not_home if they are not in the current data
                for mac in self.known_devices:
                    if mac not in updated_devices:
                        _LOGGER.info(f"Device with MAC: {mac} is no longer in the API response. Marking as not_home.")
                        updated_devices[mac] = {"mac": mac, "status": "not_home"}

                # Update the known devices
                self.known_devices = updated_devices
                return updated_devices
        except Exception as e:
            _LOGGER.error("Error fetching data from Juniper Mist API: %s", e)
            raise UpdateFailed(f"Error fetching data: {e}")

    async def async_cleanup(self):
        """Cleanup resources."""
        await self.session.close()
