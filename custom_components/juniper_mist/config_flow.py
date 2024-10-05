import voluptuous as vol
from homeassistant import config_entries
import aiohttp
from homeassistant.exceptions import HomeAssistantError 
from homeassistant.core import callback

from .const import DOMAIN, CONF_SITE_ID, CONF_API_KEY, ERROR_INVALID_AUTH, ERROR_NO_CONNECTION, US_API_URL, EU_API_URL, CONF_API_REGION, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL


class JuniperMistConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Juniper Mist."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            site_id = user_input.get(CONF_SITE_ID)
            api_key = user_input.get(CONF_API_KEY)
            api_region = user_input.get(CONF_API_REGION)

            try:
                await self._async_validate_credentials(site_id, api_key, api_region)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "no_connection"
            except Exception:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title="Juniper Mist", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_SITE_ID): str,
            vol.Required(CONF_API_KEY): str,
            vol.Required(CONF_API_REGION, default=US_API_URL): vol.In({US_API_URL: "US", EU_API_URL: "EU"})
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def _async_validate_credentials(self, site_id: str, api_key: str, api_region: str):
        """Validate the user credentials by making a test API call."""
        url = f"{api_region}/api/v1/sites/{site_id}/stats/clients"
        headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json",
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 401:
                        raise InvalidAuth
                    elif response.status != 200:
                        raise CannotConnect
        except aiohttp.ClientError as exc:
            _LOGGER.error("Error connecting to Juniper Mist API: %s", exc)
            raise CannotConnect from exc

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return JuniperMistOptionsFlowHandler(config_entry)


class InvalidAuth(HomeAssistantError):
    """Error to indicate invalid authentication."""


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class JuniperMistOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for Juniper Mist."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        scan_interval = self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        data_schema = vol.Schema({
            vol.Required(CONF_SCAN_INTERVAL, default=scan_interval): vol.Coerce(int)
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema
        )
