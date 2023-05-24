"""eess_prices sensor platform."""
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
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EESSpricesCoordinator
from .const import (
    CONF_GAS_TYPE,
    CONF_MUNICIPIO,
    CONF_MUNICIPIO_GAS_TYPE,
    CONF_MUNICIPIO_ID,
    DOMAIN,
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
    """Set up the eess_prices sensor from config entry."""
    coordinator = hass.data[DOMAIN][config.entry_id]
    sensor = EESSPriceSensor(
        coordinator,
        SENSOR_TYPES[0],
        config)
    async_add_entities([sensor])

class EESSPriceSensor(CoordinatorEntity[EESSpricesCoordinator], SensorEntity):
    """Class to hold the cheapest price of fuel given a location as a sensor."""

    def __init__(
        self,
        coordinator: EESSpricesCoordinator,
        description: SensorEntityDescription,
        config: ConfigEntry,
    ) -> None:
        """Initialize eess_prices sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = config.unique_id
        self._municipio = self.coordinator.config_entry.data[CONF_MUNICIPIO]
        self._municipio_gas_type = CONF_GAS_TYPE[self.coordinator.config_entry.data[CONF_MUNICIPIO_GAS_TYPE]]
        self._attr_name = f"{self._municipio} {self._municipio_gas_type}"
        self.entity_description = description

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return the extra state attributes"""
        return self._attributes

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()
        _LOGGER.debug("Setup for eess_prices sensor %s (%s) and %s fuel type",
                      self._municipio,
                      self.unique_id,
                      self._municipio_gas_type)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._state = self.coordinator.data["state"]
        self._attributes = self.coordinator.data["attributes"]
        self.async_write_ha_state()
        _LOGGER.debug("Updated eess_prices sensor %s (%s) and %s fuel type",
                      self._municipio,
                      self.unique_id,
                      self._municipio_gas_type)
