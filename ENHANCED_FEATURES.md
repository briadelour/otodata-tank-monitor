# Enhanced Features - Version 1.0.0

## What's New in This Version

This version of the Otodata Tank Monitor integration includes significant enhancements based on the actual Otodata API structure:

### 🎯 Enhanced Sensors

#### 1. Tank Level Sensors (Enhanced)
**Previous**: Basic level percentage only  
**Now**: Comprehensive tank information including:
- Level percentage (0-100%)
- Tank capacity in gallons
- Custom tank names from your Nee-Vo app
- Serial number
- Company information
- Product type
- Owner status
- Notification thresholds (2 levels)
- Last reading timestamp (properly parsed)

#### 2. Tank Pressure Sensors (NEW!)
**Automatically created for tanks with pressure monitoring:**
- Real-time pressure readings
- Automatic conversion from kPa to PSI
- Supports both Canadian (kPa) and US (PSI) tanks
- Device class: pressure
- State class: measurement
- Includes original kPa value as attribute

#### 3. Propane Price Sensor
**Enhanced with complete state coverage:**
- All 50 US states supported
- Regional averages available
- National average available
- 35+ state-specific URLs pre-configured

### 📊 Complete API Data Support

The integration now parses and exposes all relevant fields from the Otodata API:

```json
{
  "Id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "CustomName": "Amerigas propane",
  "SerialNumber": 28056596,
  "Level": 39,
  "TankCapacity": 1211.2,
  "LastReadingDate": "/Date(1768421163920-0500)/",
  "Product": "Propane",
  "IsOwner": true,
  "CompanyName": "Amerigas",
  "CompanySupportPhoneNumber": "1-800-XXX-XXXX",
  "TankLastPressure": 150.5,
  "TankPressureDisplayUnitSymbol": "kPa",
  "NotifyAt1": 40,
  "NotifyAt2": 20,
  "NotifyCriticalLevels": true,
  "NotifyFillDetection": true,
  "NotifyDispatch": false,
  "Latitude": 0,
  "Longitude": 0
}
```

### 🌍 International Support

**Canadian Users:**
- Automatic kPa to PSI conversion
- Preserves original kPa values in attributes
- Proper handling of Canadian tank monitors
- All features work identically for Canadian accounts

**US Users:**
- Native PSI support
- 35+ state-specific pricing URLs
- Regional pricing averages
- National average pricing

### 📍 All Supported States for Pricing

The integration includes URLs for:

**New England (6 states):**
- Connecticut, Maine, Massachusetts, New Hampshire, Rhode Island, Vermont

**Mid-Atlantic (6 states + DC):**
- Delaware, DC, Maryland, New Jersey, New York, Pennsylvania

**Southeast (4 states):**
- Florida, Georgia, North Carolina, Virginia

**South (4 states):**
- Alabama, Arkansas, Mississippi, Texas

**Midwest (15 states):**
- Illinois, Indiana, Iowa, Kansas, Kentucky, Michigan, Minnesota, Missouri, Nebraska, North Dakota, Ohio, Oklahoma, South Dakota, Tennessee, Wisconsin

**Mountain (4 states):**
- Colorado, Idaho, Montana, Utah

**Plus Regional Averages:**
- US National Average
- East Coast (PADD 1)
- Midwest (PADD 2)
- Gulf Coast (PADD 3)
- Rocky Mountain (PADD 4)

### 🔧 Technical Enhancements

#### Date Parsing
- Properly parses Otodata's date format: `/Date(1768421163920-0500)/`
- Converts to ISO 8601 format for Home Assistant
- Handles timezone offsets correctly
- Graceful fallback for missing dates

#### Pressure Conversion
- Automatic kPa to PSI conversion using factor: 0.145038
- Rounded to 2 decimal places for readability
- Original unit preserved in attributes
- Only creates pressure sensor when data is available

#### Custom Naming
- Uses your custom tank names from Nee-Vo app
- Falls back to "Tank 1", "Tank 2" if no custom name
- Maintains unique IDs based on tank UUID
- Consistent naming across restarts

#### Unique Identification
- Uses actual tank UUID for unique_id
- Prevents duplicate entities
- Survives integration reloads
- Maintains entity history

### 📱 Mobile App Integration

The setup flow includes:
- Direct links to iOS App Store
- Direct links to Google Play Store
- Instructions about the alpha-numeric code
- Guidance on registering as home owner
- Complete state pricing URL list

### 🎨 Attribute Details

#### Tank Level Sensor Attributes:
```yaml
level: 39                              # Current percentage
tank_capacity: 1211.2                  # Gallons
last_reading_date: "2026-01-14T10:26:03"  # ISO format
serial_number: 28056596                # Monitor S/N
custom_name: "Amerigas propane"       # Your custom name
company_name: "Amerigas"              # Provider
product: "Propane"                    # Fuel type
is_owner: true                        # Owner status
notify_at_level_1: 40                 # First alert %
notify_at_level_2: 20                 # Second alert %
tank_pressure: 150.5                  # Raw pressure
pressure_unit: "kPa"                  # Original unit
tank_pressure_psi: 21.83              # Converted PSI
propane_price: "2.45"                 # Current price
```

#### Pressure Sensor Attributes:
```yaml
state: 21.83                          # PSI (converted)
pressure_kpa: 150.5                   # Original kPa
original_unit: "kPa"                  # Source unit
```

### 🚀 Performance Optimizations

- **Single API Call**: Fetches all tank data in one request
- **Efficient Parsing**: Minimal processing overhead
- **Smart Updates**: Only fetches pricing once per coordinator update
- **Error Handling**: Graceful degradation if pressure or pricing unavailable
- **Logging**: Detailed debug logs for troubleshooting

### 🔐 Privacy & Security

- Tank IDs are obfuscated in logs
- Credentials stored in Home Assistant secure storage
- No sensitive data in entity attributes
- Pressure data only exposed if available
- Company phone numbers not exposed in attributes

### 📈 Use Cases Enabled

With these enhanced attributes, you can now:

1. **Track pressure trends** over time
2. **Monitor company service** quality
3. **Set up multi-level alerts** based on notification thresholds
4. **Calculate fill costs** using capacity and pricing
5. **Estimate days remaining** based on historical usage
6. **Compare regional pricing** using different state URLs
7. **Monitor Canadian tanks** with automatic unit conversion

### 🔄 Upgrade Path

If you're upgrading from a YAML-based setup:
1. Remove YAML configuration
2. Install integration via HACS
3. Configure through UI
4. All sensors will be recreated with enhanced attributes
5. Custom tank names will be preserved
6. Pressure sensors will appear automatically

### 📝 Example Automations

#### Alert on High Pressure:
```yaml
automation:
  - alias: "High Tank Pressure Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.neevo_tank_1_pressure
        above: 250
    action:
      - service: notify.mobile_app
        data:
          message: "Tank pressure is high: {{ states('sensor.neevo_tank_1_pressure') }} PSI"
```

#### Price Drop Notification:
```yaml
automation:
  - alias: "Propane Price Drop"
    trigger:
      - platform: state
        entity_id: sensor.propane_price
    condition:
      - "{{ trigger.to_state.state | float < trigger.from_state.state | float }}"
    action:
      - service: notify.mobile_app
        data:
          message: "Propane price dropped to ${{ states('sensor.propane_price') }}/gal!"
```

### 🎯 Coming Soon

Planned enhancements for future versions:
- Historical data tracking
- Fill detection notifications
- Integration with Home Assistant Energy dashboard
- Cost tracking and estimates
- Usage rate calculations
- Multiple account support

### 🐛 Known Limitations

- Latitude/Longitude data is not currently exposed (typically 0 in API)
- Company phone numbers not included in attributes (privacy)
- Dispatch notifications managed through Nee-Vo app only
- Pricing updates limited to EIA update frequency (weekly)

### 💡 Tips

1. **Custom Names**: Set meaningful names in the Nee-Vo app - they'll appear in Home Assistant
2. **Pressure Monitoring**: Not all tank monitors report pressure - this is normal
3. **Pricing Regions**: Use regional averages if your specific state isn't listed
4. **Canadian Tanks**: Pressure automatically converts to PSI, original kPa in attributes
5. **Alert Thresholds**: Your Nee-Vo app notification levels are visible as attributes

## Support

For questions about these enhanced features:
- Check the [README](README.md) for usage examples
- Review [EXAMPLES.md](EXAMPLES.md) for automation ideas
- Open an [issue](https://github.com/briadelour/otodata-tank-monitor/issues) for bugs
- Visit [Home Assistant Community](https://community.home-assistant.io/) for help

---

**Version**: 1.0.0  
**Release Date**: January 2026  
**API Version**: Otodata v1  
**Min HA Version**: 2023.8.0
