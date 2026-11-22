"""Support for Otodata Tank Monitor sensors."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import logging
import re
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
    RestoreSensor,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPressure, UnitOfVolume
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.start import async_at_started
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_PRICING_URL,
    CONF_SCAN_INTERVAL,
    CONF_SPIKE_THRESHOLD,
    API_URL,
    API_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SPIKE_THRESHOLD,
    DELIVERY_MIN_PERCENT,
    EVENT_TANK_FILLED,
    CUBIC_FEET_TO_GALLONS,
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


def parse_neevo_date_utc(date_str: str | None) -> datetime | None:
    """Like parse_neevo_date, but returns a timezone-aware UTC datetime."""
    if not date_str:
        return None
    match = re.search(r"/Date\((\d+)([+-]\d{4})?\)/", date_str)
    if not match:
        return None
    try:
        return datetime.fromtimestamp(int(match.group(1)) / 1000, tz=timezone.utc)
    except (ValueError, OverflowError, OSError):
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
            
            # Cubic feet remaining sensor (informational, liquid volume)
            entities.append(OtodataTankCubicFeetSensor(coordinator, entry, idx))

            # Gas consumption sensor - use THIS one for the Energy dashboard
            entities.append(OtodataTankConsumptionSensor(coordinator, entry, idx))

            # Last delivery (fill) sensor, fed by the consumption sensor's event
            entities.append(
                OtodataLastDeliverySensor(
                    entry,
                    tank_data.get("Id", "unknown"),
                    tank_data.get("CustomName") or f"Tank {idx + 1}",
                )
            )
            
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

        scan_minutes = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_minutes),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch tank data (and the optional EIA price) from the cloud."""
        try:
            async with asyncio.timeout(API_TIMEOUT):
                async with self.session.get(API_URL, auth=self.auth) as response:
                    if response.status != 200:
                        raise UpdateFailed(
                            f"Error communicating with API: {response.status}"
                        )
                    tanks_data = await response.json()
        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        result: dict[str, Any] = {"tanks": tanks_data}

        pricing_url = self.entry.data.get(CONF_PRICING_URL)
        if pricing_url:
            result["propane_price"] = await self._async_fetch_price(pricing_url)

        return result

    async def _async_fetch_price(self, pricing_url: str) -> str | None:
        """Fetch the EIA page and return the residential propane price ($/gal)."""
        eia_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        try:
            async with asyncio.timeout(60):
                async with self.session.get(
                    pricing_url, headers=eia_headers
                ) as price_response:
                    if price_response.status != 200:
                        _LOGGER.warning(
                            "EIA price fetch returned status %s", price_response.status
                        )
                        return None
                    price_html = await price_response.text()
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.warning("Could not fetch propane price: %s", err)
            return None

        # Parsing is CPU-bound; keep it off the event loop.
        return await self.hass.async_add_executor_job(
            self._parse_price_from_html, price_html
        )

    @staticmethod
    def _parse_price_from_html(html: str) -> str | None:
        """Parse the residential propane price ($/gal) from an EIA state page.

        The row is found by its "Residential Propane" label so a change in row
        order does not break it. If the label is not found, fall back to the
        original positional selector (5th data row, "Current2" cell).
        EIA publishes weekly Oct-Mar and monthly otherwise, and some periods
        have no value ("NA"); those return None.
        """
        try:
            soup = BeautifulSoup(html, "html.parser")

            candidates = []
            for row in soup.select("tr.DataRow"):
                label = row.get_text(" ", strip=True).lower()
                if "residential propane" in label:
                    candidates = row.select("td.Current2")
                    break

            if not candidates:
                candidates = soup.select("tr.DataRow:nth-child(5) td.Current2")

            if candidates:
                text = candidates[0].get_text(strip=True)
                float(text)  # reject "NA", "--", blanks
                return text
        except (ValueError, AttributeError) as err:
            _LOGGER.debug("Could not parse propane price: %s", err)
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
                attrs["tank_capacity_gallons"] = round(capacity_liters / GALLONS_TO_LITERS, 2)
            
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
        self._attr_device_class = SensorDeviceClass.VOLUME_STORAGE
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
        # VOLUME_STORAGE + MEASUREMENT keeps this out of the Energy dashboard
        # gas picker. Use "Gas Consumption" for Energy instead.
        self._attr_device_class = SensorDeviceClass.VOLUME_STORAGE
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



class OtodataTankCubicFeetSensor(CoordinatorEntity, SensorEntity):
    """Tank volume remaining in ft³ (liquid volume). Informational only.

    This value goes DOWN as propane is used, so do not use it as the Energy
    dashboard gas source. Use the Gas Consumption sensor.
    """

    LITERS_TO_CUBIC_FEET = 0.0353147

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

        self._attr_unique_id = f"{entry.entry_id}_cubic_feet_{tank_id}"
        self._attr_name = f"{tank_name} Cubic Feet Remaining"
        # VOLUME_STORAGE + MEASUREMENT keeps this out of the Energy dashboard
        # gas picker. Use "Gas Consumption" for Energy instead.
        self._attr_device_class = SensorDeviceClass.VOLUME_STORAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfVolume.CUBIC_FEET
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
                liters_remaining = (level / 100) * capacity_liters
                cubic_feet_remaining = liters_remaining * self.LITERS_TO_CUBIC_FEET
                return round(cubic_feet_remaining, 2)
        return None


class OtodataTankConsumptionSensor(CoordinatorEntity, RestoreSensor):
    """Tracks cumulative propane consumption in ft³ for the HA energy dashboard.

    On each coordinator update, if the tank volume has decreased, the delta is
    added to a running total. Increases (deliveries) are ignored. The total is
    persisted across HA restarts via RestoreSensor, and resets to zero on a
    fresh install.
    """

    LITERS_TO_CUBIC_FEET = 0.0353147
    # Ignore tiny fluctuations smaller than this (sensor noise / rounding)
    MIN_DELTA_FT3 = 0.01
    # Seconds to wait after Home Assistant has started before counting usage
    # that happened while it was down (see async_added_to_hass).
    STARTUP_CATCH_UP_DELAY = 60

    def __init__(
        self,
        coordinator: OtodataUpdateCoordinator,
        entry: ConfigEntry,
        tank_index: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._tank_index = tank_index
        self._unsub_start = None
        self._unsub_delay = None
        # A large drop waiting for a second, different reading to confirm it:
        # (volume_ft3, reading marker). None when nothing is being held.
        self._held_drop: tuple[float, str | None] | None = None
        self._spike_percent: int = entry.options.get(
            CONF_SPIKE_THRESHOLD, DEFAULT_SPIKE_THRESHOLD
        )
        self._cumulative_consumption: float = 0.0
        self._previous_volume_ft3: float | None = None

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

        self._tank_id = tank_id
        self._tank_name = tank_name
        self._attr_unique_id = f"{entry.entry_id}_consumption_{tank_id}"
        self._attr_name = f"{tank_name} Gas Consumption"
        self._attr_device_class = SensorDeviceClass.GAS
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = UnitOfVolume.CUBIC_FEET
        self._attr_icon = "mdi:fire"

    async def async_added_to_hass(self) -> None:
        """Restore state and previous volume on HA startup."""
        await super().async_added_to_hass()

        # Restore cumulative consumption total
        last_sensor_data = await self.async_get_last_sensor_data()
        if last_sensor_data and last_sensor_data.native_value is not None:
            try:
                self._cumulative_consumption = float(last_sensor_data.native_value)
                _LOGGER.debug(
                    "Restored consumption total: %.3f ft³", self._cumulative_consumption
                )
            except (ValueError, TypeError):
                self._cumulative_consumption = 0.0

        # Restore previous volume so first update calculates delta correctly
        last_state = await self.async_get_last_state()
        if last_state and last_state.attributes.get("previous_volume_ft3") is not None:
            try:
                self._previous_volume_ft3 = float(
                    last_state.attributes["previous_volume_ft3"]
                )
            except (ValueError, TypeError):
                self._previous_volume_ft3 = None

        if self._previous_volume_ft3 is None:
            # Fresh install: just record the starting volume. Nothing to add.
            self._process_current_volume()
            return

        # The coordinator's first fetch happens before this entity exists, so
        # no update callback fires for it. Usage that happened across a restart
        # or reload is therefore counted shortly after startup instead of
        # waiting for the next poll. It is deliberately NOT counted right now:
        # the Energy dashboard's cost sensor treats the first value it sees as
        # its starting point, so the restored total must be published first
        # and the catch-up applied afterwards, as a normal increase it can price.
        self.async_on_remove(self._cancel_catch_up)
        self._unsub_start = async_at_started(self.hass, self._async_start_catch_up)

    @callback
    def _async_start_catch_up(self, _hass: HomeAssistant) -> None:
        """Home Assistant has started: schedule the catch-up after a short delay."""
        self._unsub_start = None
        self._unsub_delay = async_call_later(
            self.hass, self.STARTUP_CATCH_UP_DELAY, self._async_catch_up
        )

    @callback
    def _async_catch_up(self, _now: datetime) -> None:
        """Count any drop that happened while Home Assistant was not running."""
        self._unsub_delay = None
        self._process_current_volume()
        self.async_write_ha_state()

    @callback
    def _cancel_catch_up(self) -> None:
        """Cancel a pending catch-up (entity removed or integration unloaded)."""
        if self._unsub_start is not None:
            self._unsub_start()
            self._unsub_start = None
        if self._unsub_delay is not None:
            self._unsub_delay()
            self._unsub_delay = None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Calculate consumption delta on each coordinator update."""
        self._process_current_volume()
        self.async_write_ha_state()

    def _process_current_volume(self) -> None:
        """Update the running total from the latest reading.

        - A drop is added to the total (usage).
        - A rise of DELIVERY_MIN_PERCENT or more fires a "tank filled" event.
        - A drop larger than the spike threshold is held until a second,
          different reading confirms it, so one bad reading (for example a
          momentary 0%) is not counted as usage.
        """
        current = self._get_current_volume_ft3()
        if current is None:
            return

        previous = self._previous_volume_ft3
        if previous is None:
            # First reading ever seen: just record it.
            self._previous_volume_ft3 = current
            return

        reading = self._get_reading_marker()
        delta = previous - current
        capacity = self._get_capacity_ft3()
        threshold_ft3 = (
            capacity * self._spike_percent / 100
            if capacity and self._spike_percent > 0
            else None
        )

        if delta > self.MIN_DELTA_FT3:
            if threshold_ft3 is not None and delta > threshold_ft3:
                if self._held_drop is None:
                    self._held_drop = (current, reading)
                    _LOGGER.warning(
                        "%s: reading dropped %.1f%% in one step; holding it until "
                        "a second reading confirms it",
                        self._tank_name,
                        delta / capacity * 100,
                    )
                    return
                if reading is not None and reading == self._held_drop[1]:
                    # Same reading as when it was held; wait for a new one.
                    return
                _LOGGER.info("%s: large drop confirmed by a second reading", self._tank_name)
            self._held_drop = None
            self._cumulative_consumption = round(self._cumulative_consumption + delta, 3)
            _LOGGER.debug(
                "Propane consumed: %.3f ft³ | Total: %.3f ft³",
                delta,
                self._cumulative_consumption,
            )
        else:
            if self._held_drop is not None:
                _LOGGER.info("%s: held drop discarded; reading recovered", self._tank_name)
            self._held_drop = None
            if delta < -self.MIN_DELTA_FT3 and capacity:
                rise_percent = (-delta) / capacity * 100
                if rise_percent >= DELIVERY_MIN_PERCENT:
                    self._fire_tank_filled(previous, current, capacity, reading)

        self._previous_volume_ft3 = current

    def _fire_tank_filled(
        self, previous: float, current: float, capacity: float, reading: str | None
    ) -> None:
        """Fire the tank-filled event with details about the delivery."""
        added_ft3 = current - previous
        gallons_added = round(added_ft3 * CUBIC_FEET_TO_GALLONS, 1)

        price_per_gallon = None
        if self.coordinator.data and self.coordinator.data.get("propane_price"):
            try:
                price_per_gallon = round(float(self.coordinator.data["propane_price"]), 3)
            except (ValueError, TypeError):
                price_per_gallon = None
        estimated_cost = (
            round(gallons_added * price_per_gallon, 2)
            if price_per_gallon is not None
            else None
        )

        when = parse_neevo_date_utc(reading) or dt_util.utcnow()
        data = {
            "tank_id": self._tank_id,
            "tank_name": self._tank_name,
            "level_before": round(previous / capacity * 100, 1),
            "level_after": round(current / capacity * 100, 1),
            "gallons_added": gallons_added,
            "price_per_gallon": price_per_gallon,
            "estimated_cost": estimated_cost,
            "delivery_time": when.isoformat(),
        }
        _LOGGER.info("%s: delivery detected: %s", self._tank_name, data)
        self.hass.bus.async_fire(EVENT_TANK_FILLED, data)

    def _get_tank_data(self) -> dict[str, Any] | None:
        """Return this tank's raw API data, if available."""
        if (
            self.coordinator.data
            and "tanks" in self.coordinator.data
            and len(self.coordinator.data["tanks"]) > self._tank_index
        ):
            return self.coordinator.data["tanks"][self._tank_index]
        return None

    def _get_reading_marker(self) -> str | None:
        """Return an identifier for the tank monitor's latest reading."""
        tank_data = self._get_tank_data()
        return tank_data.get("LastReadingDate") if tank_data else None

    def _get_capacity_ft3(self) -> float | None:
        """Return the tank's total capacity in ft³ (liquid volume)."""
        tank_data = self._get_tank_data()
        if tank_data and tank_data.get("TankCapacity") is not None:
            return tank_data["TankCapacity"] * self.LITERS_TO_CUBIC_FEET
        return None

    def _get_current_volume_ft3(self) -> float | None:
        """Return current tank volume in ft³."""
        if (
            self.coordinator.data
            and "tanks" in self.coordinator.data
            and len(self.coordinator.data["tanks"]) > self._tank_index
        ):
            tank_data = self.coordinator.data["tanks"][self._tank_index]
            level = tank_data.get("Level")
            capacity_liters = tank_data.get("TankCapacity")
            if level is not None and capacity_liters is not None:
                liters_remaining = (level / 100) * capacity_liters
                return round(liters_remaining * self.LITERS_TO_CUBIC_FEET, 3)
        return None

    @property
    def native_value(self) -> float:
        """Return cumulative gas consumption in ft³."""
        return self._cumulative_consumption

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose previous volume (restored on restart) and any held reading."""
        attrs: dict[str, Any] = {"previous_volume_ft3": self._previous_volume_ft3}
        if self._held_drop is not None:
            attrs["held_drop_volume_ft3"] = self._held_drop[0]
        return attrs

class OtodataLastDeliverySensor(RestoreSensor):
    """Time of the most recent delivery (fill), with details as attributes.

    Updated from the tank-filled event the consumption sensor fires, and
    restored after a restart. Reads only; nothing is written to Otodata.
    """

    _attr_should_poll = False
    _DETAIL_KEYS = (
        "level_before",
        "level_after",
        "gallons_added",
        "price_per_gallon",
        "estimated_cost",
    )

    def __init__(self, entry: ConfigEntry, tank_id: str, tank_name: str) -> None:
        """Initialize the sensor."""
        self._tank_id = tank_id
        self._attr_unique_id = f"{entry.entry_id}_last_delivery_{tank_id}"
        self._attr_name = f"{tank_name} Last Delivery"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:truck-delivery"
        self._attr_native_value = None
        self._details: dict[str, Any] = {}

    async def async_added_to_hass(self) -> None:
        """Restore the last delivery and listen for new ones."""
        await super().async_added_to_hass()

        last_data = await self.async_get_last_sensor_data()
        if last_data and isinstance(last_data.native_value, datetime):
            self._attr_native_value = last_data.native_value

        last_state = await self.async_get_last_state()
        if last_state:
            if self._attr_native_value is None:
                parsed = dt_util.parse_datetime(last_state.state)
                if parsed is not None:
                    self._attr_native_value = parsed
            self._details = {
                key: last_state.attributes[key]
                for key in self._DETAIL_KEYS
                if last_state.attributes.get(key) is not None
            }

        self.async_on_remove(
            self.hass.bus.async_listen(EVENT_TANK_FILLED, self._handle_tank_filled)
        )

    @callback
    def _handle_tank_filled(self, event) -> None:
        """Record a delivery reported for this tank."""
        data = event.data
        if data.get("tank_id") != self._tank_id:
            return
        when = dt_util.parse_datetime(data.get("delivery_time") or "")
        self._attr_native_value = when or dt_util.utcnow()
        self._details = {k: data.get(k) for k in self._DETAIL_KEYS}
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the delivery details."""
        return dict(self._details)


class OtodataPropanePriceSensor(CoordinatorEntity, RestoreSensor):
    """Residential propane price from EIA, expressed in USD/ft³.

    EIA publishes weekly Oct-Mar and monthly otherwise, and some periods have
    no value. When no fresh price is available the last good price is kept
    (and restored after a restart) so Energy dashboard cost keeps working.
    The ``price_is_stale`` attribute is true while an old price is in use.
    """

    # 1 gallon = 0.133681 ft³, so $/gal × 7.48052 = USD/ft³
    _GAL_TO_FT3 = 7.48052

    def __init__(
        self,
        coordinator: OtodataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_propane_price"
        self._attr_name = "Propane Price"
        self._attr_native_unit_of_measurement = "USD/ft³"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:currency-usd"
        self._last_value: float | None = self._compute_value()
        self._is_stale = False

    async def async_added_to_hass(self) -> None:
        """Restore the last price if no fresh price is available yet."""
        await super().async_added_to_hass()
        if self._last_value is None:
            last_data = await self.async_get_last_sensor_data()
            if last_data and last_data.native_value is not None:
                try:
                    self._last_value = float(last_data.native_value)
                    self._is_stale = True
                except (ValueError, TypeError):
                    self._last_value = None

    def _compute_value(self) -> float | None:
        """Convert the EIA $/gal price to USD/ft³, or None if unavailable."""
        if self.coordinator.data and "propane_price" in self.coordinator.data:
            price_str = self.coordinator.data["propane_price"]
            if price_str:
                try:
                    return round(float(price_str) * self._GAL_TO_FT3, 4)
                except (ValueError, TypeError):
                    return None
        return None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Keep the newest good price; flag it stale if only an old one exists."""
        value = self._compute_value()
        if value is not None:
            self._last_value = value
            self._is_stale = False
        else:
            self._is_stale = self._last_value is not None
        self.async_write_ha_state()

    @property
    def native_value(self) -> float | None:
        """Return the price in USD/ft³."""
        return self._last_value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose the per-gallon price and whether it is stale."""
        per_gallon = (
            round(self._last_value / self._GAL_TO_FT3, 4)
            if self._last_value is not None
            else None
        )
        return {"price_per_gallon": per_gallon, "price_is_stale": self._is_stale}
