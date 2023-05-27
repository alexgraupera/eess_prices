"""eess_prices sensor platform."""
from __future__ import annotations

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
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EESSpricesCoordinator
from .const import (
    CONF_FUEL_TYPE,
    CONF_MUNICIPIO,
    CONF_MUNICIPIO_FUEL_TYPE,
    CONF_MUNICIPIO_ID,
    DOMAIN,
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MUNICIPIO): cv.string,
        vol.Required(CONF_MUNICIPIO_ID): vol.All(vol.Coerce(int)),
        vol.Required(CONF_MUNICIPIO_FUEL_TYPE): vol.In(CONF_FUEL_TYPE)
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
        SENSOR_TYPES[0])
    async_add_entities([sensor])

class EESSPriceSensor(CoordinatorEntity[EESSpricesCoordinator], SensorEntity):
    """Class to hold the cheapest price of fuel given a location as a sensor."""

    def __init__(
        self,
        coordinator: EESSpricesCoordinator,
        description: SensorEntityDescription
    ) -> None:
        """Initialize eess_prices sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = self.coordinator.config_entry.unique_id
        self._municipio = self.coordinator.config_entry.data[CONF_MUNICIPIO]
        self._municipio_fuel_type = CONF_FUEL_TYPE[self.coordinator.config_entry.data[CONF_MUNICIPIO_FUEL_TYPE]]
        self._attr_name = f"{self._municipio} {self._municipio_fuel_type}"
        self.entity_description = description

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()
        _LOGGER.debug("Setup for eess_prices sensor %s (%s) and %s fuel type",
                      self._municipio,
                      self.unique_id,
                      self._municipio_fuel_type)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data["state"]
        self._attr_extra_state_attributes = self.coordinator.data["attributes"]
        self.async_write_ha_state()
        _LOGGER.debug("Updated eess_prices sensor %s (%s) and %s fuel type",
                      self._municipio,
                      self.unique_id,
                      self._municipio_fuel_type)
