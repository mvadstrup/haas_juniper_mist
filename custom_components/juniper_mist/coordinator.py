import logging
from datetime import timedelta
import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import CONF_SITE_ID, CONF_API_KEY, CONF_API_REGION, DOMAIN

_LOGGER = logging.getLogger(__name__)

class JuniperMistDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch data from Juniper Mist API."""

    def __init__(self, hass, config_entry):
        """Initialize the coordinator."""
        self.site_id = config_entry.data[CONF_SITE_ID]
        self.api_key = config_entry.data[CONF_API_KEY]
        self.api_region = config_entry.data[CONF_API_REGION]
        self.session = aiohttp.ClientSession()
        self.known_devices = {}  # Keep track of known devices
        self.wx_tags = []  # Store WX tags

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=300),  # 5 minutes
        )
        _LOGGER.info("JuniperMistDataUpdateCoordinator initialized for site ID: %s", self.site_id)

    async def _async_update_data(self):
        """Fetch data from Juniper Mist API."""
        client_url = f"{self.api_region}/api/v1/sites/{self.site_id}/stats/clients"
        wx_tag_url = f"{self.api_region}/api/v1/sites/{self.site_id}/wxtags"
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }

        _LOGGER.info("Attempting to fetch data from Juniper Mist API for site ID: %s", self.site_id)
        try:
            # Fetch client data
            async with self.session.get(client_url, headers=headers) as response:
                if response.status != 200:
                    text = await response.text()
                    _LOGGER.error("Client API returned a non-200 status: %s", response.status)
                    raise UpdateFailed(f"Client API returned status {response.status}: {text}")
                client_data = await response.json()

            # Fetch WX tag data
            async with self.session.get(wx_tag_url, headers=headers) as response:
                if response.status != 200:
                    text = await response.text()
                    _LOGGER.error("WX tags API returned a non-200 status: %s", response.status)
                    raise UpdateFailed(f"WX tags API returned status {response.status}: {text}")
                self.wx_tags = await response.json()

            _LOGGER.info("Data successfully fetched from Juniper Mist API for site ID: %s", self.site_id)

            # Process client data and match WX tags by MAC address
            updated_devices = {client["mac"]: self._merge_wx_tag_with_client(client) for client in client_data if isinstance(client, dict)}

            # Set previously known devices to not_home if they are not in the current data
            for mac in self.known_devices:
                if mac not in updated_devices:
                    _LOGGER.info(f"Device with MAC: {mac} is no longer in the API response. Marking as not_home.")
                    updated_devices[mac] = {"mac": mac, "status": "not_home"}

            # Update the known devices
            self.known_devices = updated_devices
            _LOGGER.info("Known devices updated successfully.")
            return updated_devices

        except aiohttp.ClientError as e:
            _LOGGER.error("Network error when fetching data: %s", e)
            raise UpdateFailed(f"Network error fetching data: {e}")

        except Exception as e:
            _LOGGER.critical("Unhandled exception during data fetch: %s", e)
            raise UpdateFailed(f"Error fetching data: {e}")

    def _merge_wx_tag_with_client(self, client):
        """Merge WX tags into client data based on MAC address."""
        mac_address = client.get("mac")
        wx_tag_name = None

        for tag in self.wx_tags:
            if tag.get("mac") == mac_address:
                wx_tag_name = tag.get("name")
                break

        if wx_tag_name:
            _LOGGER.info(f"WX tag '{wx_tag_name}' found for device MAC: {mac_address}. Updating name.")
            client["hostname"] = wx_tag_name  # Use WX tag name as hostname

        return client

    async def async_cleanup(self):
        """Cleanup resources."""
        _LOGGER.info("Cleaning up the aiohttp session.")
        await self.session.close()
