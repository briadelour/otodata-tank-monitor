"""Support for Otodata Tank Monitor sensors."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
import re
from typing import Any

import aiohttp
import async_timeout

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPressure, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_PRICING_URL,
    API_URL,
    API_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    KPA_TO_PSI,
    GALLONS_TO_LITERS,
    ATTR_LEVEL,
    ATTR_LAST_READING,
    ATTR_TANK_CAPACITY,
    ATTR_PROPANE_PRICE,
    ATTR_SERIAL_NUMBER,
    ATTR_CUSTOM_NAME,
    ATTR_COMPANY_NAME,
    ATTR_NOTIFY_AT_1,
    ATTR_NOTIFY_AT_2,
    ATTR_TANK_PRESSURE,
    ATTR_PRESSURE_UNIT,
    ATTR_IS_OWNER,
    ATTR_PRODUCT,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=DEFAULT_SCAN_INTERVAL)


def parse_neevo_date(date_str: str | None) -> datetime | None:
    """Parse Otodata's date format: /Date(1768421163920-0500)/"""
    if not date_str:
        return None
    
    try:
        # Extract timestamp from /Date(1768421163920-0500)/ format
        match = re.search(r'/Date\((\d+)([+-]\d{4})?\)/', date_str)
        if match:
            timestamp_ms = int(match.group(1))
            # Convert milliseconds to seconds
            return datetime.fromtimestamp(timestamp_ms / 1000)
    except (ValueError, AttributeError) as err:
        _LOGGER.debug("Could not parse date %s: %s", date_str, err)
    
    return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Otodata sensors based on a config entry."""
    coordinator = OtodataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entities = []
    
    # Create sensors for each tank found
    if coordinator.data and "tanks" in coordinator.data:
        for idx, tank_data in enumerate(coordinator.data["tanks"]):
            # Main tank level sensor
            entities.append(OtodataTankSensor(coordinator, entry, idx))
            
            # Gallons remaining sensor
            entities.append(OtodataTankGallonsSensor(coordinator, entry, idx))
            
            # Liters remaining sensor
            entities.append(OtodataTankLitersSensor(coordinator, entry, idx))
            
            # Tank pressure sensor (if available)
            if tank_data.get("TankLastPressure") is not None:
                entities.append(OtodataTankPressureSensor(coordinator, entry, idx))
    
    # Add propane price sensor if URL is configured
    if entry.data.get(CONF_PRICING_URL):
        entities.append(OtodataPropanePriceSensor(coordinator, entry))

    async_add_entities(entities)


class OtodataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Otodata tank data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.entry = entry
        self.session = async_get_clientsession(hass)
        self.auth = aiohttp.BasicAuth(
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            async with async_timeout.timeout(API_TIMEOUT):
                async with self.session.get(
                    API_URL,
                    auth=self.auth,
                ) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Error communicating with API: {response.status}")
                    
                    tanks_data = await response.json()
                    
                    result = {"tanks": tanks_data}
                    
                    # Fetch propane price if URL is configured
                    pricing_url = self.entry.data.get(CONF_PRICING_URL)
                    if pricing_url:
                        try:
                            async with async_timeout.timeout(30):
                                async with self.session.get(pricing_url) as price_response:
                                    if price_response.status == 200:
                                        price_html = await price_response.text()
                                        result["propane_price"] = self._parse_price_from_html(price_html)
                        except Exception as err:
                            _LOGGER.warning("Could not fetch propane price: %s", err)
                            result["propane_price"] = None
                    
                    return result

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    def _parse_price_from_html(self, html: str) -> str | None:
        """Parse propane price from EIA HTML page."""
        try:
            # Look for the current price in the third data row
            import re
            # This regex looks for price patterns like "$2.45" or "2.45"
            pattern = r'DataRow.*?Current2.*?\$?([\d.]+)'
            match = re.search(pattern, html, re.DOTALL)
            if match:
                return match.group(1)
        except Exception as err:
            _LOGGER.debug("Error parsing propane price: %s", err)
        return None


class OtodataTankSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Neevo Tank level sensor."""

    def __init__(
        self,
        coordinator: OtodataUpdateCoordinator,
        entry: ConfigEntry,
        tank_index: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._tank_index = tank_index
        
        # Get tank ID for unique_id (obfuscated in logs)
        tank_id = "unknown"
        if (
            coordinator.data
            and "tanks" in coordinator.data
            and len(coordinator.data["tanks"]) > tank_index
        ):
            tank_data = coordinator.data["tanks"][tank_index]
            tank_id = tank_data.get("Id", "unknown")
            # Use custom name or serial number for friendly name
            custom_name = tank_data.get("CustomName")
            if custom_name:
                self._attr_name = custom_name
            else:
                self._attr_name = f"Neevo Tank {tank_index + 1}"
        else:
            self._attr_name = f"Neevo Tank {tank_index + 1}"
        
        self._attr_unique_id = f"{entry.entry_id}_tank_{tank_id}"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:propane-tank"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if (
            self.coordinator.data
            and "tanks" in self.coordinator.data
            and len(self.coordinator.data["tanks"]) > self._tank_index
        ):
            tank_data = self.coordinator.data["tanks"][self._tank_index]
            return tank_data.get("Level")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if (
            self.coordinator.data
            and "tanks" in self.coordinator.data
            and len(self.coordinator.data["tanks"]) > self._tank_index
        ):
            tank_data = self.coordinator.data["tanks"][self._tank_index]
            
            # Parse the last reading date
            last_reading = parse_neevo_date(tank_data.get("LastReadingDate"))
            
            # Get capacity (API returns in liters)
            capacity_liters = tank_data.get("TankCapacity")
            
            attrs = {
                ATTR_LEVEL: tank_data.get("Level"),
                ATTR_TANK_CAPACITY: capacity_liters,  # Original from API (liters)
                "tank_capacity_liters": capacity_liters,  # Explicit liters
                ATTR_SERIAL_NUMBER: tank_data.get("SerialNumber"),
                ATTR_CUSTOM_NAME: tank_data.get("CustomName"),
                ATTR_COMPANY_NAME: tank_data.get("CompanyName"),
                ATTR_PRODUCT: tank_data.get("Product"),
                ATTR_IS_OWNER: tank_data.get("IsOwner"),
                ATTR_NOTIFY_AT_1: tank_data.get("NotifyAt1"),
                ATTR_NOTIFY_AT_2: tank_data.get("NotifyAt2"),
            }
            
            # Add tank capacity in gallons for clarity
            if capacity_liters is not None:
                attrs["tank_capacity_gallons"] = round(capacity_liters / GALLONS_TO_LITERS, 1)
            
            # Add formatted last reading date
            if last_reading:
                attrs[ATTR_LAST_READING] = last_reading.isoformat()
            
            # Add pressure information if available
            if tank_data.get("TankLastPressure") is not None:
                pressure = tank_data.get("TankLastPressure")
                pressure_unit = tank_data.get("TankPressureDisplayUnitSymbol", "kPa")
                attrs[ATTR_TANK_PRESSURE] = pressure
                attrs[ATTR_PRESSURE_UNIT] = pressure_unit
                
                # Convert kPa to PSI if needed
                if pressure_unit == "kPa" and pressure is not None:
                    attrs["tank_pressure_psi"] = round(pressure * KPA_TO_PSI, 2)
            
            # Add propane price if available
            if "propane_price" in self.coordinator.data:
                attrs[ATTR_PROPANE_PRICE] = self.coordinator.data["propane_price"]
            
            return attrs
        return {}


class OtodataTankPressureSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Neevo Tank pressure sensor."""

    def __init__(
        self,
        coordinator: OtodataUpdateCoordinator,
        entry: ConfigEntry,
        tank_index: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._tank_index = tank_index
        
        # Get tank ID and name
        tank_id = "unknown"
        tank_name = f"Tank {tank_index + 1}"
        if (
            coordinator.data
            and "tanks" in coordinator.data
            and len(coordinator.data["tanks"]) > tank_index
        ):
            tank_data = coordinator.data["tanks"][tank_index]
            tank_id = tank_data.get("Id", "unknown")
            custom_name = tank_data.get("CustomName")
            if custom_name:
                tank_name = custom_name
        
        self._attr_unique_id = f"{entry.entry_id}_pressure_{tank_id}"
        self._attr_name = f"{tank_name} Pressure"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_class = SensorDeviceClass.PRESSURE
        self._attr_icon = "mdi:gauge"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if (
            self.coordinator.data
            and "tanks" in self.coordinator.data
            and len(self.coordinator.data["tanks"]) > self._tank_index
        ):
            tank_data = self.coordinator.data["tanks"][self._tank_index]
            pressure = tank_data.get("TankLastPressure")
            pressure_unit = tank_data.get("TankPressureDisplayUnitSymbol", "kPa")
            
            if pressure is not None:
                # Convert to PSI for Home Assistant (standard pressure unit)
                if pressure_unit == "kPa":
                    return round(pressure * KPA_TO_PSI, 2)
                else:
                    return pressure
        return None

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        # Always return PSI as that's what we convert to
        return UnitOfPressure.PSI

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if (
            self.coordinator.data
            and "tanks" in self.coordinator.data
            and len(self.coordinator.data["tanks"]) > self._tank_index
        ):
            tank_data = self.coordinator.data["tanks"][self._tank_index]
            pressure = tank_data.get("TankLastPressure")
            pressure_unit = tank_data.get("TankPressureDisplayUnitSymbol", "kPa")
            
            attrs = {}
            if pressure is not None and pressure_unit == "kPa":
                attrs["pressure_kpa"] = pressure
                attrs["original_unit"] = pressure_unit
            
            return attrs
        return {}


class OtodataTankGallonsSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Neevo Tank gallons remaining sensor."""

    def __init__(
        self,
        coordinator: OtodataUpdateCoordinator,
        entry: ConfigEntry,
        tank_index: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._tank_index = tank_index
        
        # Get tank ID and name
        tank_id = "unknown"
        tank_name = f"Tank {tank_index + 1}"
        if (
            coordinator.data
            and "tanks" in coordinator.data
            and len(coordinator.data["tanks"]) > tank_index
        ):
            tank_data = coordinator.data["tanks"][tank_index]
            tank_id = tank_data.get("Id", "unknown")
            custom_name = tank_data.get("CustomName")
            if custom_name:
                tank_name = custom_name
        
        self._attr_unique_id = f"{entry.entry_id}_gallons_{tank_id}"
        self._attr_name = f"{tank_name} Gallons Remaining"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfVolume.GALLONS
        self._attr_icon = "mdi:gauge"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if (
            self.coordinator.data
            and "tanks" in self.coordinator.data
            and len(self.coordinator.data["tanks"]) > self._tank_index
        ):
            tank_data = self.coordinator.data["tanks"][self._tank_index]
            level = tank_data.get("Level")
            capacity_liters = tank_data.get("TankCapacity")  # API returns capacity in liters
            
            if level is not None and capacity_liters is not None:
                # Calculate liters remaining first
                liters_remaining = (level / 100) * capacity_liters
                # Convert to gallons
                gallons_remaining = liters_remaining / GALLONS_TO_LITERS
                return round(gallons_remaining, 1)
        return None


class OtodataTankLitersSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Neevo Tank liters remaining sensor."""

    def __init__(
        self,
        coordinator: OtodataUpdateCoordinator,
        entry: ConfigEntry,
        tank_index: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._tank_index = tank_index
        
        # Get tank ID and name
        tank_id = "unknown"
        tank_name = f"Tank {tank_index + 1}"
        if (
            coordinator.data
            and "tanks" in coordinator.data
            and len(coordinator.data["tanks"]) > tank_index
        ):
            tank_data = coordinator.data["tanks"][tank_index]
            tank_id = tank_data.get("Id", "unknown")
            custom_name = tank_data.get("CustomName")
            if custom_name:
                tank_name = custom_name
        
        self._attr_unique_id = f"{entry.entry_id}_liters_{tank_id}"
        self._attr_name = f"{tank_name} Liters Remaining"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfVolume.LITERS
        self._attr_icon = "mdi:gauge"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if (
            self.coordinator.data
            and "tanks" in self.coordinator.data
            and len(self.coordinator.data["tanks"]) > self._tank_index
        ):
            tank_data = self.coordinator.data["tanks"][self._tank_index]
            level = tank_data.get("Level")
            capacity_liters = tank_data.get("TankCapacity")  # API returns capacity in liters
            
            if level is not None and capacity_liters is not None:
                # Capacity is already in liters, just calculate remaining
                liters_remaining = (level / 100) * capacity_liters
                return round(liters_remaining, 1)
        return None


class OtodataPropanePriceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Neevo Propane Price sensor."""

    def __init__(
        self,
        coordinator: OtodataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_propane_price"
        self._attr_name = "Propane Price"
        self._attr_native_unit_of_measurement = "$/gal"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:currency-usd"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data and "propane_price" in self.coordinator.data:
            price_str = self.coordinator.data["propane_price"]
            if price_str:
                try:
                    return float(price_str)
                except (ValueError, TypeError):
                    return None
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.native_value is not None
