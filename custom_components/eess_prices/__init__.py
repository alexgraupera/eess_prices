"""The ess_prices integration to collect best carburant station prices for a spain municipality."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_MUNICIPIO,
    CONF_MUNICIPIO_FILTER_URL,
    CONF_MUNICIPIO_GAS_TYPE,
    CONF_MUNICIPIO_ID,
    DOMAIN,
    KEY_GAS_TYPE,
    KEY_LISTA_EESS_PRECIO,
    KEY_STATION_ADDRESS,
    KEY_STATION_LATITUDE,
    KEY_STATION_LONGITUDE,
    KEY_STATION_NAME,
    KEY_STATION_OPENING_HOURS,
)

PLATFORMS: list[str] = ["sensor"]
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = EESSpricesCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def options_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True

class EESSpricesCoordinator(DataUpdateCoordinator):
    """Coordinator is responsible for querying the device at a specified route."""
    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialise a custom coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=30),
        )
        self._session = async_get_clientsession(hass)
        self._municipio = entry.data[CONF_MUNICIPIO]
        self._municipio_id = entry.data[CONF_MUNICIPIO_ID]
        self._municipio_gas_type = entry.data[CONF_MUNICIPIO_GAS_TYPE]
        
    async def _async_update_data(self) -> dict:
        url = f"{CONF_MUNICIPIO_FILTER_URL}{self._municipio_id}"
        async with self._session.get(url) as response:
            data = await response.json()
        service_stations = {}
        for service_station in data[KEY_LISTA_EESS_PRECIO]:
            gas_type = KEY_GAS_TYPE[self._municipio_gas_type]
            if gas_type in service_station:
                price = service_station[gas_type]
                if price:
                    name = service_station[KEY_STATION_NAME]
                    coordinates = (float(service_station[KEY_STATION_LATITUDE].replace(',', '.')), float(service_station[KEY_STATION_LONGITUDE].replace(',', '.')))
                    opening_hours = service_station[KEY_STATION_OPENING_HOURS]
                    price = float(price.replace(',', '.'))
                    address = service_station[KEY_STATION_ADDRESS]
                    service_stations[name] = {'coordinates': coordinates, 'address': address, 'opening_hours': opening_hours, 'price': price}
        if service_stations:
            service_station = min(service_stations, key=lambda x: service_stations[x]['price'])
            return {
                "state": service_stations[service_station]["price"],
                "attributes": {
                    "latitude": service_stations[service_station]["coordinates"][0],
                    "longitude": service_stations[service_station]["coordinates"][1],
                    "name": service_station,
                    "address": service_stations[service_station]["address"],
                    "opening_hours": service_stations[service_station]["opening_hours"],
                    "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
        return None