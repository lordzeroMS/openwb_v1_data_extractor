# openWB Home Assistant Integration

This project provides a custom [Home Assistant](https://www.home-assistant.io/) integration for an openWB charging system. It polls the built-in REST API (`/openWB/web/api.php?get=all`) and exposes every reported value as a Home Assistant sensor.

## Installation

1. Copy the `custom_components/openwb` directory into the `custom_components` folder of your Home Assistant configuration.
2. Restart Home Assistant to load the integration.

## Configuration

1. In Home Assistant, go to **Settings → Devices & Services → Add Integration**.
2. Search for **openWB**.
3. Enter the host or full URL of your openWB controller (for example `192.168.1.168` or `http://192.168.1.168`).
4. Optionally provide a human-friendly name for the installation.

After setup, the integration automatically creates sensors for every key/value pair returned by the API. Newly discovered keys are added as sensors without requiring user action.

## Notes

- The integration polls the API every 30 seconds.
- Sensor values are automatically cast to numeric types whenever possible; otherwise the raw string value is used.
- If the openWB API becomes unreachable, the sensors are marked as unavailable until the connection is restored.
