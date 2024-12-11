"""Config flow for Audi connect integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from audiconnectpy import MODELS, AudiConnect, AudiException, AuthorizationError
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_PIN, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import (
    API_LEVEL_CHARGER,
    API_LEVEL_CLIMATISATION,
    API_LEVEL_LOCK,
    API_LEVEL_VENTILATION,
    API_LEVEL_WINDOWSHEATING,
    CONF_COUNTRY,
    CONF_MODEL,
    CONF_SCAN_INTERVAL,
    CONF_VEHICLE,
    COUNTRY_CODE,
    DEFAULT_MODEL,
    DOMAIN,
    MENU_OTHER,
    MENU_SAVE,
    MENU_VEHICLES,
)

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_COUNTRY, default="DE"): vol.In(COUNTRY_CODE),
        vol.Optional(CONF_PIN): str,
        vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): vol.In(MODELS),
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Audi connect."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Get option flow."""
        return OptionsFlowHandler()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                self._async_abort_entries_match(
                    {
                        CONF_USERNAME: user_input[CONF_USERNAME],
                    },
                )
                api = AudiConnect(
                    async_create_clientsession(self.hass),
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input[CONF_COUNTRY],
                    user_input.get(CONF_PIN),
                    model=user_input[CONF_MODEL],
                )
                await api.async_login()
                if not api.is_connected:
                    raise AuthorizationError(
                        "Unexpected error communicating with the Audi server"
                    )

            except AuthorizationError:
                errors["base"] = "invalid_auth"
            except AudiException:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="Audi connect", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle option."""

    def __init__(self) -> None:
        """Initialize the options flow."""
        self._sel = None
        self._data = {}

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,  # pylint: disable=unused-argument
    ) -> FlowResult:
        """Handle options flow."""
        return self.async_show_menu(
            step_id="init", menu_options=[MENU_VEHICLES, MENU_OTHER, MENU_SAVE]
        )

    async def async_step_vehicles(self, user_input=None) -> FlowResult:
        """Select vehicle."""
        if user_input is not None:
            self._sel = user_input[CONF_VEHICLE]
            return await self.async_step_apilevel()

        dev_reg = dr.async_get(self.hass)
        entries = dr.async_entries_for_config_entry(dev_reg, self.config_entry.entry_id)
        dev_ids = {
            identifier[1]: entry.name
            for entry in entries
            for identifier in entry.identifiers
            if identifier[0] == DOMAIN
        }
        data_schema = vol.Schema(
            {
                vol.Required(CONF_VEHICLE): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        options=[
                            selector.SelectOptionDict(value=vin, label=name)
                            for vin, name in dev_ids.items()
                        ],
                    )
                )
            }
        )
        return self.async_show_form(
            step_id="vehicles", data_schema=data_schema, last_step=False
        )

    async def async_step_other(self, user_input=None) -> FlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_init()

        data_schema = self.add_suggested_values_to_schema(
            vol.Schema(
                {
                    vol.Required(CONF_SCAN_INTERVAL): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=5, step=1, mode=selector.NumberSelectorMode.BOX
                        )
                    )
                }
            ),
            self.config_entry.options,
        )

        return self.async_show_form(
            step_id="other", data_schema=data_schema, last_step=False
        )

    async def async_step_apilevel(self, user_input=None) -> FlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self._data.update({self._sel: user_input})
            return await self.async_step_init()

        api_level = self.config_entry.options.get(self._sel, {})

        data_schema = self.add_suggested_values_to_schema(
            vol.Schema(
                {
                    vol.Required(
                        API_LEVEL_CLIMATISATION,
                        default=api_level.get(API_LEVEL_CLIMATISATION, "2"),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            options=[
                                selector.SelectOptionDict(value="2", label="Level 2"),
                                selector.SelectOptionDict(value="3", label="Level 3"),
                            ],
                        )
                    ),
                    vol.Required(
                        API_LEVEL_VENTILATION,
                        default=api_level.get(API_LEVEL_VENTILATION, "1"),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            options=[
                                selector.SelectOptionDict(value="1", label="Level 1"),
                                selector.SelectOptionDict(value="2", label="Level 2"),
                            ],
                        )
                    ),
                    vol.Required(
                        API_LEVEL_CHARGER,
                        default=api_level.get(API_LEVEL_CHARGER, "1"),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            options=[
                                selector.SelectOptionDict(value="1", label="Level 1"),
                                selector.SelectOptionDict(value="2", label="Level 2"),
                                selector.SelectOptionDict(value="2", label="Level 3"),
                            ],
                        )
                    ),
                    vol.Required(
                        API_LEVEL_WINDOWSHEATING,
                        default=api_level.get(API_LEVEL_WINDOWSHEATING, "1"),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            options=[
                                selector.SelectOptionDict(value="1", label="Level 1"),
                                selector.SelectOptionDict(value="2", label="Level 2"),
                            ],
                        )
                    ),
                    vol.Required(
                        API_LEVEL_LOCK,
                        default=api_level.get(API_LEVEL_LOCK, "1"),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            options=[
                                selector.SelectOptionDict(value="1", label="Level 1")
                            ],
                        )
                    ),
                }
            ),
            self.config_entry.options,
        )

        return self.async_show_form(
            step_id="apilevel", data_schema=data_schema, last_step=False
        )

    async def async_step_save(self, user_input=None) -> FlowResult:
        """Save and exit."""
        return self.async_create_entry(title="", data=self._data)
