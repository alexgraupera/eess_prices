"""Config flow for EESS prices."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries, core
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_FUEL_TYPE,
    CONF_MUNICIPIO,
    CONF_MUNICIPIO_FUEL_TYPE,
    CONF_MUNICIPIO_FUEL_TYPE_DESCRIPTION,
    CONF_MUNICIPIO_ID,
    CONF_MUNICIPIOS_URL_LIST,
    DOMAIN,
)

DATA_SCHEMA = vol.Schema(
    { 
        vol.Required(CONF_MUNICIPIO_ID, default=1): vol.All(vol.Coerce(int), vol.Range(min=1)),
        vol.Required(CONF_MUNICIPIO, default=""): vol.All(str, vol.Length(min=1)),
        vol.Required(CONF_MUNICIPIO_FUEL_TYPE): vol.In(CONF_FUEL_TYPE)
    }
)

class EESSPricesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    municipalities = {}

    async def async_step_user(self, user_input):
        if user_input is not None:
            municipio_id = user_input.get(CONF_MUNICIPIO_ID)
            municipio = self.municipalities[municipio_id]
            municipio_fuel_type = user_input.get(CONF_MUNICIPIO_FUEL_TYPE)
            municipio_fuel_type_description = CONF_FUEL_TYPE[municipio_fuel_type]
            sensor_title = f"{municipio} {municipio_fuel_type_description}"
            unique_id_key = f"{user_input.get(CONF_MUNICIPIO_ID)}_{user_input.get(CONF_MUNICIPIO_FUEL_TYPE)}"

            await self.async_set_unique_id(unique_id_key)
            self._abort_if_unique_id_configured()
            user_input[CONF_MUNICIPIO] = municipio
            user_input[CONF_MUNICIPIO_FUEL_TYPE_DESCRIPTION] = municipio_fuel_type_description

            return self.async_create_entry(title=sensor_title, data=user_input)

        self.municipalities = await async_get_municipios(self.hass)
        self.municipalities = dict(sorted(self.municipalities.items(), key=lambda x: x[1]))
        return self.async_show_form(step_id="user", data_schema=vol.Schema(
                    {
                        vol.Required(CONF_MUNICIPIO_ID): vol.In(self.municipalities),
                        vol.Required(CONF_MUNICIPIO_FUEL_TYPE): vol.In(CONF_FUEL_TYPE)
                    }
                ))

async def async_get_municipios(hass: core.HomeAssistant):
    url = CONF_MUNICIPIOS_URL_LIST
    async with async_get_clientsession(hass) as session:
        async with session.get(url) as response:
            data = await response.json()
            return {municipio["IDMunicipio"]: municipio["Municipio"] for municipio in data}