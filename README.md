# Juniper Mist Custom Integration for Home Assistant

This is a custom integration that allows Home Assistant to connect to Juniper Mist's API and track devices connected to the network.

## Features

- Tracks devices connected to a Juniper Mist network via the API.
- Displays devices in the `device_tracker` entity.
- Provides real-time device information such as IP address, MAC address, signal strength, and more.
- Automatically updates devices' home/not_home status based on connection data from the API.

## Installation

1. Copy the `juniper_mist` folder to your Home Assistant `custom_components` directory:
   ```
   custom_components/juniper_mist/
   ```

2. Restart Home Assistant.

3. Navigate to **Settings** > **Devices & Services** > **Integrations**, and click the "Add Integration" button.

4. Search for "Juniper Mist" and follow the instructions to authenticate using your Juniper Mist API Key and Site ID.

## Configuration

The integration requires two configuration parameters:

- **API Key**: Your Juniper Mist API key, which you can generate in the Mist dashboard.
- **Site ID**: The ID of the site you want to monitor, found in your Mist dashboard URL.

You can set up the integration through the Home Assistant UI. No YAML configuration is required.

## Entities

The integration creates `device_tracker` entities for each device connected to the Juniper Mist network. The entity will show:
- Device name or MAC address
- Connection status (`home` or `not_home`)
- Signal strength (RSSI)
- IP address and other network-related information.

## Notes

- The integration polls the Juniper Mist API every 5 minutes to retrieve device status.
- A device is considered `home` if it has been recently seen or has an active connection.
- If a device doesn't appear in the API response for over 5 minutes, it is marked as `not_home`.
- Upon reloading the integration, devices not connected will temporarily be marked as `unavailable` until they reconnect to the network.

## Future Plans

I plan to expand this integration to support location services, enabling more advanced tracking features, such as geofencing and proximity detection. 

**P.S.**: If you happen to be affiliated with Juniper and have an extra access point and a long-term license for location services lying around, please don't hesitate to reach out! :)

## Troubleshooting

- Ensure that your API key and site ID are correct.
- Check the Home Assistant logs for any errors related to API connection issues or authentication.

## Credits

This custom integration was developed for Home Assistant to enable seamless tracking of Juniper Mist connected devices.

