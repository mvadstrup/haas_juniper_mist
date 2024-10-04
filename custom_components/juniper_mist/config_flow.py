import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
import logging

from .const import DOMAIN, CONF_SITE_ID, CONF_API_KEY, ERROR_INVALID_AUTH, ERROR_NO_CONNECTION

_LOGGER = logging.getLogger(__name__)

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
            try:
                await self._async_validate_credentials(site_id, api_key)
            except InvalidAuth:
                errors["base"] = ERROR_INVALID_AUTH
            except CannotConnect:
                errors["base"] = ERROR_NO_CONNECTION
            except Exception:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title="Juniper Mist", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_SITE_ID): str,
            vol.Required(CONF_API_KEY): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def _async_validate_credentials(self, site_id: str, api_key: str):
        """Validate the user credentials by making a test API call."""
        url = f"https://api.eu.mist.com/api/v1/sites/{site_id}/stats/clients"
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

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
