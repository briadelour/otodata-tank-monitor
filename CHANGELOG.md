# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Custom update intervals
- Multiple account support
- Advanced alerting options
- Integration with Home Assistant Energy dashboard

---

## Version History

- **1.0.0** - Initial HACS-compatible release
