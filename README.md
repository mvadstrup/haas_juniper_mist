# Juniper Mist Custom Integration for Home Assistant

![Juniper Mist Logo](icons/logo.png)

This is a custom integration that allows Home Assistant to connect to Juniper Mist's API and track devices connected to the network.

## Features

- Tracks devices connected to a Juniper Mist network via the API.
- Displays devices in the `device_tracker` entity.
- Provides real-time device information such as IP address, MAC address, signal strength, and more.
- Automatically updates devices' home/not_home status based on connection data from the API.

## Installation

### Via HACS (Home Assistant Community Store)

1. Ensure that you have [HACS](https://hacs.xyz/) installed in your Home Assistant setup.
2. In Home Assistant, navigate to **HACS** > **Integrations**.
3. Click on the three dots in the top right corner and select **Custom repositories**.
4. In the **Repository** field, enter:

   ```
   https://github.com/mvadstrup/haas_juniper_mist
   ```

5. Set the **Category** to **Integration**.
6. Click **Add**.
7. After adding the repository, find **Juniper Mist** in the list of integrations in HACS and click **Download** or **Install**.
8. Restart Home Assistant to load the new integration.

### Manual Installation

1. Copy the `juniper_mist` folder to your Home Assistant `custom_components` directory:

   ```
   custom_components/juniper_mist/
   ```

2. Restart Home Assistant.

## Configuration

1. Navigate to **Settings** > **Devices & Services** > **Integrations**, and click the **Add Integration** button.
2. Search for **Juniper Mist** and select it.
3. Follow the on-screen instructions to authenticate using your Juniper Mist **API Key** and **Site ID**.

### Required Parameters

- **API Key**: Your Juniper Mist API key, which you can generate in the Mist dashboard.
- **Site ID**: The ID of the site you want to monitor, found in your Mist dashboard URL.

## Entities

The integration creates `device_tracker` entities for each device connected to the Juniper Mist network. The entity will show:

- Device name or MAC address
- Connection status (`home` or `not_home`)
- Signal strength (RSSI)
- IP address and other network-related information

## Notes

- The integration polls the Juniper Mist API every 5 minutes to retrieve device status.
- A device is considered `home` if it has been recently seen or has an active connection.
- If a device doesn't appear in the API response for over 5 minutes, it is marked as `not_home`.
- Upon reloading the integration, devices not connected will temporarily be marked as `unavailable` until they reconnect to the network.

## Enabling Debug Logging

To troubleshoot issues with the Juniper Mist integration, you can enable debug logging in Home Assistant. Follow these steps:

1. Open your `configuration.yaml` file.
2. Add the following lines to enable debug logging for the Juniper Mist integration:

   ```yaml
   logger:
     default: info
     logs:
       custom_components.juniper_mist: debug
   ```

3. Restart Home Assistant to apply the logging changes.
4. Check the logs by going to **Settings** > **System** > **Logs**.

This will enable detailed logs for the integration, helping you diagnose connection or API-related issues.

## Future Plans

I plan to expand this integration to support location services, enabling more advanced tracking features such as geofencing and proximity detection.

**P.S.** If you happen to be affiliated with Juniper and have an extra access point and a long-term license for location services lying around, please don't hesitate to reach out! :)

## Troubleshooting

- Ensure that your API key and Site ID are correct.
- Check the Home Assistant logs for any errors related to API connection issues or authentication.

