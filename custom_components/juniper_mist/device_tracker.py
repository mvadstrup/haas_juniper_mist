import logging
from homeassistant.components.device_tracker import SourceType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import callback
from .images import PICTURE_ITEMS
from homeassistant.const import ATTR_ENTITY_PICTURE
import time
from .const import DOMAIN

# Initialize the logger
_LOGGER = logging.getLogger(__name__)

class JuniperMistDeviceTracker(CoordinatorEntity, RestoreEntity):
    """Represents a device tracked by Juniper Mist."""

    def __init__(self, coordinator, client_data):
        """Initialize the device tracker."""
        super().__init__(coordinator)
        self.client_data = client_data
        self.mac = client_data.get("mac")
        self._attr_unique_id = self.mac
        self._attr_name = client_data.get("hostname") or self.mac
        self._attr_device_class = "connectivity"
        self._attr_source_type = SourceType.ROUTER
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.mac)},
            manufacturer=client_data.get("manufacture"),
            name=self._attr_name,
            model=self.client_data.get("model") or "Unknown",
            sw_version=self.client_data.get("os") or "Unknown",
        )
        _LOGGER.info("Initialized Juniper Mist device tracker for MAC: %s", self.mac)

    async def async_added_to_hass(self):
        """Restore the previous state if necessary."""
        await super().async_added_to_hass()

        # Attempt to restore the previous state
        if (last_state := await self.async_get_last_state()) is not None:
            _LOGGER.info("Restoring last state for MAC: %s", self.mac)
            # Restore the last known state
            #self.client_data['last_seen'] = last_state.attributes.get('last_seen', self.client_data.get('last_seen'))
            self.client_data['ip'] = last_state.attributes.get('ip_address', self.client_data.get('ip'))

    @property
    def state(self):
        """Return the state of the device."""
        last_seen = self.client_data.get("last_seen")
        uptime = self.client_data.get("uptime")
        current_time = time.time()

        # Consider device home if last seen within the last 5 minutes (300 seconds)
        if last_seen and (current_time - last_seen) <= 300:
            _LOGGER.info(f"Device {self.mac} is considered home (recent activity, last seen {last_seen} - diff ({current_time - last_seen})).")
            return "home"

        # Consider device home if uptime is recent (device is actively connected)
        if uptime and uptime > 300 and last_seen and (current_time - last_seen) >= 300:
            _LOGGER.info(f"Device {self.mac} is considered home (uptime {uptime} indicates active connection).")
            return "home"


        # Otherwise, mark as not home
        _LOGGER.info(f"Device {self.mac} is not home (no recent activity or connection).")
        return "not_home"


    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        return {
            "mac_address": self.client_data.get("mac"),
            "hostname": self.client_data.get("hostname"),
            "ip_address": self.client_data.get("ip"),
            "ssid": self.client_data.get("ssid"),
            "last_seen": self.client_data.get("last_seen"),
            "rssi": self.client_data.get("rssi"),
            "snr": self.client_data.get("snr"),
            "band": self.client_data.get("band"),
            "channel": self.client_data.get("channel"),
            "vlan_id": self.client_data.get("vlan_id"),
            "proto": self.client_data.get("proto"),
            "idle_time": self.client_data.get("idle_time"),
            "tx_rate": self.client_data.get("tx_rate"),
            "rx_rate": self.client_data.get("rx_rate"),
            ATTR_ENTITY_PICTURE: PICTURE_ITEMS.get("logo"),
        }

    async def async_update(self):
        """Update the entity with new data from the coordinator."""
        _LOGGER.info("Updating Juniper Mist device tracker for MAC: %s", self.mac)
        self.client_data = self._get_client_data()
        self.async_write_ha_state()

    def _get_client_data(self):
        """Retrieve the latest client data from the coordinator."""
        data = self.coordinator.data
        for client in data:
            if isinstance(client, dict) and client.get("mac") == self.mac:
                return client
        _LOGGER.error("Failed to find client data for MAC: %s. Marking as not_home.", self.mac)
        return {"mac": self.mac, "status": "not_home"}

async def async_setup_entry(hass, entry, async_add_entities: AddEntitiesCallback):
    """Set up device_tracker entities from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Initialize a set to keep track of existing MAC addresses
    if "entities" not in hass.data[DOMAIN]:
        hass.data[DOMAIN]["entities"] = set()

    new_entities = []

    # Log the data received from the coordinator
    _LOGGER.info("Data from coordinator: %s", coordinator.data)

    # Iterate over the data which is a dictionary where the key is the MAC address
    for mac, client in coordinator.data.items():
        # Ensure that the client is a dictionary
        if isinstance(client, dict):
            if mac not in hass.data[DOMAIN]["entities"]:
                entity = JuniperMistDeviceTracker(coordinator, client)
                new_entities.append(entity)
                hass.data[DOMAIN]["entities"].add(mac)
        else:
            _LOGGER.error("Unexpected client format for MAC: %s", mac)

    if new_entities:
        _LOGGER.info("Adding new device trackers for Juniper Mist")
        async_add_entities(new_entities)

    # Define a listener to handle new clients dynamically
    @callback
    def handle_update():
        """Handle updated data from the coordinator."""
        new_entities = []
        for mac, client in coordinator.data.items():
            # Ensure that the client is a dictionary
            if isinstance(client, dict):
                if mac not in hass.data[DOMAIN]["entities"]:
                    entity = JuniperMistDeviceTracker(coordinator, client)
                    new_entities.append(entity)
                    hass.data[DOMAIN]["entities"].add(mac)
            else:
                _LOGGER.error("Unexpected client format during update for MAC: %s", mac)

        if new_entities:
            _LOGGER.info("Handling dynamic update for new clients in Juniper Mist")
            async_add_entities(new_entities)

    coordinator.async_add_listener(handle_update)
