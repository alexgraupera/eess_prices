"""GitHub sensor platform."""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta
import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO, UnitOfVolume
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EESSpricesCoordinator

from .const import (
    DOMAIN,
    CONF_MUNICIPIO,
    CONF_MUNICIPIO_ID,
    CONF_MUNICIPIO_GAS_TYPE,
    CONF_GAS_TYPE
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MUNICIPIO): cv.string,
        vol.Required(CONF_MUNICIPIO_ID): vol.All(vol.Coerce(int)),
        vol.Required(CONF_MUNICIPIO_GAS_TYPE): vol.In(CONF_GAS_TYPE)
    }
)

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1
SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="EESSPrices",
        icon="mdi:gas-station",
        native_unit_of_measurement=f"{CURRENCY_EURO}/{UnitOfVolume.LITERS}",
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

async def async_setup_entry(
    hass: HomeAssistant, 
    config: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][config.entry_id]
    sensor = EESSPriceSensor(
        coordinator,
        SENSOR_TYPES[0],
        config)
    async_add_entities([sensor])

class EESSPriceSensor(CoordinatorEntity[EESSpricesCoordinator], SensorEntity):
    def __init__(
        self,
        coordinator: EESSpricesCoordinator,
        description: SensorEntityDescription,
        config: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = config.unique_id
        self._attr_name = f"{config.data[CONF_MUNICIPIO]} {CONF_GAS_TYPE[config.data[CONF_MUNICIPIO_GAS_TYPE]]}"
        self.entity_description = description

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return self._attributes

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._state = self.coordinator.data["state"]
        self._attributes = self.coordinator.data["attributes"]
        self.async_write_ha_state()
