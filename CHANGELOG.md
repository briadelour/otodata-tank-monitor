# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-11-14

Major release: adds proper Energy dashboard support and fixes several issues found while testing with a refilled tank. Requires Home Assistant 2024.11.0 or later.

### Added
- **Gas Consumption sensor** (`<tank> Gas Consumption`): cumulative propane used, in ft³ (liquid volume), for the Energy dashboard. Tank volume decreases are added to the total; increases (deliveries) are ignored. Survives restarts.
- **Cubic Feet Remaining sensor** (informational).
- **Configurable update interval** under the integration's **Configure** button (15 to 1440 minutes).
- **Propane Price** attributes `price_per_gallon` and `price_is_stale`.
- **ENERGY_DASHBOARD.md**: setup guide, unit explanation, limitations for tanks that are refilled by delivery, and troubleshooting.

### Changed (breaking)
- **Gallons, Liters and Cubic Feet Remaining** now use device class `volume_storage` and state class `measurement` (were `gas`/`total` for liters and cubic feet). They no longer appear in the Energy dashboard gas picker, which previously let users select a falling value and see negative usage. Home Assistant may flag their old statistics; use **Developer Tools → Statistics → Fix issue**. If one was your Energy gas source, switch to **Gas Consumption**.
- **Default update interval is now 6 hours** (360 minutes), down from a fixed 24 hours, so a reading can lag by about the device's report interval plus 6 hours instead of plus 24. Existing installs pick this up automatically.
- **Liters Remaining** now displays in liters. It was shown in ft³ on US unit systems because of the old `gas` device class.
- Minimum Home Assistant version is now 2024.11.0 (options flow API).

### Fixed
- **Propane Price** now finds the "Residential Propane" row by label instead of a fixed row position, falls back to the old position, and rejects non-numeric values such as `NA`.
- **Propane Price** keeps the last good price (and restores it after a restart) when EIA has no fresh value, instead of becoming `unknown` and dropping Energy cost to $0. EIA publishes weekly only October through March.
- Declared the `beautifulsoup4` requirement in `manifest.json`. Without it the price could silently stay `unknown`.
- Setup form now shows "invalid username or password" and "no devices found" instead of always reporting a connection error.
- The EIA price fetch no longer runs inside the Otodata request's 30-second timeout, and price parsing no longer blocks the event loop.
- `strings.json` was empty; it now matches `translations/en.json`.
- Documentation: clarified that the integration reads only the tank's current state and does not import history from the Nee-Vo app; corrected entity IDs, capacity units (the API reports liters), the price unit (USD/ft³), install paths (`otodata_tank_monitor`), and the Mushroom card gallons formula.

### Known limitations
- Usage is stamped with the time of the poll, not the time propane was burned.
- If propane is used and a delivery arrives between two polls, the two changes net out and a little usage is not counted.
- Tank level is reported in whole percent, so 1% of tank capacity is the smallest step.

## [1.3.0] - 2026-05-19

### Fixed
- fixed gas consumption for energy dashboard compatiblity

## [1.2.2] - 2026-05-18

### Fixed
- Fixed price and cubic ft

## [1.2.1] - 2026-05-18

### Fixed
- refactored parsing of price from html

## [1.2.0] - 2026-05-18

### Fixed
- updated device class for gas

## [1.1.2] - 2026-05-18

### Fixed
- Refactored price parsing for NC

## [1.1.1] - 2026-01-16

### Fixed
- **CRITICAL BUG**: Fixed incorrect volume calculations. The API returns `TankCapacity` in liters, not gallons. Previous version incorrectly treated capacity as gallons, resulting in calculated values that were 3.78541x too high (e.g., showing 448 gallons instead of 118 gallons for a 320-gallon tank at 37%).
  - Gallons sensor now correctly converts: `(level / 100) × capacity_liters ÷ 3.78541`
  - Liters sensor now directly calculates: `(level / 100) × capacity_liters`
  - Added `tank_capacity_gallons` and `tank_capacity_liters` attributes to main sensor for clarity

### Changed
- Enhanced main tank sensor attributes to explicitly show capacity in both liters (from API) and gallons (calculated)

## [1.0.0] - 2026-01-15

### Added
- Initial release of Otodata Propane Tank Monitor integration
- UI-based configuration flow (no YAML required)
- Support for multiple tank monitoring
- Real-time tank level sensor with percentage reading
- **Tank volume sensors: gallons and liters remaining**
- **Tank pressure sensors with automatic kPa to PSI conversion**
- **Enhanced tank attributes (12+ data points per tank)**
- **Support for Canadian tanks with kPa pressure units**
- **Custom tank naming from Nee-Vo mobile app**
- Optional propane pricing sensor using EIA data
- **Complete US state coverage (35+ states) for pricing**
- **Regional pricing averages (PADD 1-4)**
- **National average pricing**
- Automatic daily updates (24-hour scan interval)
- **Proper date parsing for Otodata's date format**
- HACS compatibility
- Comprehensive documentation and installation guide
- Example automations for low tank alerts
- Dashboard card examples (gauge, entity cards)
- Support for basic authentication with Otodata API
- **UUID-based unique entity IDs for stability**
- Integration validation workflow for HACS

### Features
- **Tank Monitoring**: Monitor propane levels from Otodata tank monitors
- **Multi-Tank Support**: Automatic detection and creation of sensors for all tanks on account
- **Volume Sensors**: Dedicated sensors for gallons and liters remaining (no templates needed!)
- **Pressure Monitoring**: Automatic pressure sensors for supported tank monitors
- **International**: Full support for Canadian tanks with kPa to PSI conversion
- **Price Tracking**: Optional integration with EIA propane pricing data for 35+ US states
- **Easy Setup**: Configuration through Home Assistant UI with validation
- **Rich Attributes**: 
  - Level, capacity, serial number
  - Custom names, company info
  - Notification thresholds
  - Pressure data (raw and converted)
  - Last reading timestamps
  - Owner status
- **Smart Naming**: Uses custom tank names from Nee-Vo app
- **Automations**: Enable low-level alerts, volume alerts, pressure monitoring, and price tracking

### Entity IDs Created Per Tank
- `sensor.{tank_name}` - Tank level percentage
- `sensor.{tank_name}_gallons_remaining` - Gallons remaining
- `sensor.{tank_name}_liters_remaining` - Liters remaining
- `sensor.{tank_name}_pressure` - Tank pressure (if supported)
- `sensor.propane_price` - Propane price (if configured)

### Technical
- **Data Coordinator**: Efficient API polling with caching
- **Date Parsing**: Converts Otodata's `/Date(...)/ ` format to ISO 8601
- **Unit Conversion**: Automatic kPa to PSI conversion (factor: 0.145038)
- **Error Handling**: Graceful degradation when optional data unavailable
- **Logging**: Comprehensive debug logging for troubleshooting

### Documentation
- README with full feature documentation
- INSTALLATION guide with step-by-step instructions
- CONTRIBUTING guidelines for developers
- Examples for dashboard cards and automations
- Troubleshooting guide

## [Unreleased]

### Planned Features
- Support for additional states' propane pricing
- Historical data tracking
- Multiple account support
- Advanced alerting options
- Delivery detection sensor/event

---

## Version History

- **2.0.0** - Energy dashboard support, configurable update interval, price and setup fixes
- **1.1.1** - Fixed volume calculations (API capacity is in liters)
- **1.0.0** - Initial HACS-compatible release
