# Otodata Tank Monitor for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/briadelour/otodata-tank-monitor.svg)](https://github.com/briadelour/otodata-tank-monitor/releases)

Monitor your Otodata propane tank levels directly in Home Assistant. Access your tank data through the Nee-Vo portal by Otodata Network. This is a custom integration that can be installed via HACS.

<div align="center">
<img width="502" height="494" alt="Otodata Tank Monitor Screenshot" src="https://github.com/user-attachments/assets/d08153cb-b5fd-43ab-8d34-5b74f099cc57" />
</div>

## Features

- **Real-time tank level monitoring** - Track your propane tank fill percentage
- **Automatic daily updates** - Sensor updates every 24 hours
- **Multiple tank support** - Monitor multiple propane tanks from one account
- **Historical data** - Access last reading date and tank capacity information
- **Optional propane pricing** - Track local propane prices from EIA data
- **Pressure monitoring** - Tank pressure sensor with automatic kPa to PSI conversion
- **Custom tank names** - Uses your custom names from the Nee-Vo mobile app
- **Alert thresholds** - View your configured notification levels
- **Easy UI configuration** - No YAML required, configure through the UI
- **HACS compatible** - Install and update easily through HACS

## API Data Structure

The integration retrieves data from the Otodata API in this format:

```json
[
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
    "TankLastPressure": 150.5,
    "TankPressureDisplayUnitSymbol": "kPa",
    "NotifyAt1": 40,
    "NotifyAt2": 20,
    "NotifyCriticalLevels": true,
    "NotifyFillDetection": true
  }
]
```

**Note:** Canadian tanks may report pressure in kPa, which is automatically converted to PSI by the integration.

## Prerequisites

Before installing this integration, you need:

1. **Home Assistant** installed and running (version 2023.8.0 or later)
2. **A Nee-Vo portal account** with active propane tank monitoring service

<div align="center">
<img width="256" height="256" alt="icon" src="https://github.com/user-attachments/assets/b32dd9af-a206-437d-80eb-68de9acb9a59" />
</div>

3. **The Nee-Vo mobile app** installed on your phone:
   - [iOS App](https://apps.apple.com/us/app/nee-vo/id1108454345)
   - [Android App](https://play.google.com/store/apps/details?id=ca.otodata.nee_vo&hl=en_US&pli=1)

## Setting Up Your Otodata Account

If you haven't already set up your Nee-Vo portal account:

1. Download and install the Nee-Vo mobile app (see links above)
2. Create a new account or sign in to an existing account
3. Locate the **alpha-numeric code** on your Nee-Vo tank monitor device
4. In the app, scan the QR code or manually enter the alpha-numeric code
5. **Register as the home owner** - You can do this even if you don't physically own the tank monitor
6. Remember your username and password - you'll need them for Home Assistant

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/briadelour/otodata-tank-monitor`
6. Select category: "Integration"
7. Click "Add"
8. Click "Install" on the Otodata Tank Monitor card
9. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/briadelour/otodata-tank-monitor/releases)
2. Extract the `custom_components/neevo` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

### Adding the Integration

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Otodata Tank Monitor"
4. Enter your Nee-Vo username and password
5. (Optional) Enter a propane pricing URL for your state
6. Click **Submit**

### Propane Pricing URLs

To track propane prices in your area, you can add an EIA (Energy Information Administration) URL during setup. The integration supports all US states and regions:

**To find your state's URL:**

1. Visit the [EIA Weekly Residential Propane Prices page](https://www.eia.gov/dnav/pet/pet_pri_wfr_a_EPM0_PRS_dpgal_w.htm)
2. Find your state in the list
3. Click on your state name
4. Copy the URL from your browser's address bar
5. Use this URL when configuring the integration

**Quick Reference - Popular States:**

| State | URL |
|-------|-----|
| **Connecticut** | `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SCT_w.htm` |
| **Maine** | `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SME_w.htm` |
| **Massachusetts** | `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SMA_w.htm` |
| **New Hampshire** | `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SNH_w.htm` |
| **New York** | `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SNY_w.htm` |
| **Pennsylvania** | `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SPA_w.htm` |
| **North Carolina** | `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SNC_w.htm` |
| **Ohio** | `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SOH_w.htm` |
| **Michigan** | `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SMI_w.htm` |
| **Illinois** | `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SIL_w.htm` |
| **Wisconsin** | `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SWI_w.htm` |
| **Vermont** | `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SVT_w.htm` |

**All Supported States:**
- **New England**: CT, ME, MA, NH, RI, VT
- **Mid-Atlantic**: DE, DC, MD, NJ, NY, PA
- **South**: FL, GA, NC, VA, AL, AR, MS, TX, KY, TN
- **Midwest**: IL, IN, IA, KS, MI, MN, MO, NE, ND, OH, OK, SD, WI
- **Mountain**: CO, ID, MT, UT

**Regional URLs** are also available:
- **US National Average**: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_nus_w.htm`
- **East Coast (PADD 1)**: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_R10_w.htm`
- **Midwest (PADD 2)**: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_R20_w.htm`
- **Gulf Coast (PADD 3)**: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_R30_w.htm`
- **Rocky Mountain (PADD 4)**: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_R40_w.htm`

The URL pattern is: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_S[STATE]_w.htm` where `[STATE]` is typically the two-letter state abbreviation.

## Usage

### Available Sensors

Once configured, the integration creates the following sensors:

#### Tank Level Sensors
- **Entity ID:** `sensor.neevo_tank_1`, `sensor.neevo_tank_2`, etc.
- **State:** Current tank fill percentage (0-100)
- **Unit:** %
- **Name:** Uses your custom tank name from the Nee-Vo app if available

#### Tank Volume Sensors
- **Gallons Remaining:**
  - **Entity ID:** `sensor.neevo_tank_1_gallons_remaining`, `sensor.neevo_tank_2_gallons_remaining`, etc.
  - **State:** Actual gallons remaining in tank
  - **Unit:** gal
  - **Calculated from:** Level % × Tank Capacity

- **Liters Remaining:**
  - **Entity ID:** `sensor.neevo_tank_1_liters_remaining`, `sensor.neevo_tank_2_liters_remaining`, etc.
  - **State:** Actual liters remaining in tank
  - **Unit:** L
  - **Calculated from:** Gallons × 3.78541

#### Tank Pressure Sensors (if available)
- **Entity ID:** `sensor.neevo_tank_1_pressure`, `sensor.neevo_tank_2_pressure`, etc.
- **State:** Current tank pressure
- **Unit:** PSI (automatically converted from kPa for Canadian tanks)
- **Note:** Only created for tanks that report pressure data

#### Propane Price Sensor (if configured)
- **Entity ID:** `sensor.propane_price`
- **State:** Current propane price per gallon
- **Unit:** $/gal

### Sensor Attributes

Each tank level sensor provides these attributes:

**Basic Information:**
- **level** - Current tank fill percentage
- **tank_capacity** - Total capacity of your propane tank (in gallons)
- **last_reading_date** - Timestamp of the last sensor reading from the tank monitor (ISO format)
- **serial_number** - Tank monitor serial number

**Tank Details:**
- **custom_name** - Your custom name for the tank (from Nee-Vo app)
- **company_name** - Your propane company name (if registered)
- **product** - Type of fuel (typically "Propane")
- **is_owner** - Whether you're registered as the home owner

**Alerts:**
- **notify_at_level_1** - First notification threshold percentage
- **notify_at_level_2** - Second notification threshold percentage

**Pressure Information** (if available):
- **tank_pressure** - Raw pressure value from sensor
- **pressure_unit** - Original unit (kPa or PSI)
- **tank_pressure_psi** - Pressure converted to PSI (for kPa tanks)

**Pricing** (if configured):
- **propane_price** - Current propane price from EIA

### Dashboard Examples

#### Gauge Card

```yaml
type: gauge
entity: sensor.neevo_tank_1
name: Propane Tank
min: 0
max: 100
severity:
  green: 50
  yellow: 25
  red: 0
```

#### Entity Card

```yaml
type: entities
entities:
  - entity: sensor.neevo_tank_1
    name: Tank Level
  - entity: sensor.neevo_tank_1_gallons_remaining
    name: Gallons Remaining
  - entity: sensor.neevo_tank_1_liters_remaining
    name: Liters Remaining
  - type: attribute
    entity: sensor.neevo_tank_1
    attribute: last_reading_date
    name: Last Reading
  - type: attribute
    entity: sensor.neevo_tank_1
    attribute: tank_capacity
    name: Tank Capacity
  - entity: sensor.propane_price
    name: Current Price
```

## Automations

### Low Tank Alert

Create an automation to notify you when the tank is low:

```yaml
automation:
  - alias: "Low Propane Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.neevo_tank_1
        below: 20
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Low Propane"
          message: "Propane tank is at {{ states('sensor.neevo_tank_1') }}%"
```

### Weekly Propane Price Notification

```yaml
automation:
  - alias: "Weekly Propane Price Update"
    trigger:
      - platform: time
        at: "09:00:00"
      - platform: state
        entity_id: sensor.propane_price
    condition:
      - condition: time
        weekday:
          - mon
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Propane Price Update"
          message: >
            Current propane price: ${{ states('sensor.propane_price') }}/gal
            Tank level: {{ states('sensor.neevo_tank_1') }}%
```

## Troubleshooting

### Sensor Shows "Unavailable"

1. Verify your Nee-Vo credentials are correct in the integration configuration
2. Check that your Nee-Vo portal account is active and has tank monitoring enabled
3. Ensure you can log in to the Nee-Vo mobile app with the same credentials
4. Review Home Assistant logs: **Settings** → **System** → **Logs**

### No Devices Found Error

1. Make sure you have registered at least one tank monitor in the Nee-Vo mobile app
2. Verify you can see your tank(s) in the Nee-Vo mobile app
3. Try removing and re-adding the integration
4. Check that you've registered as the home owner in the Nee-Vo app

### Wrong Tank is Being Monitored

If you have multiple tanks, the integration will create a sensor for each tank. Make sure you're looking at the correct sensor entity (`sensor.neevo_tank_1`, `sensor.neevo_tank_2`, etc.)

### Sensor Not Updating

- The sensor updates every 24 hours by default
- You can force an update by reloading the integration: **Settings** → **Devices & Services** → **Otodata** → **⋮** → **Reload**
- Check the `last_reading_date` attribute to see when Otodata last received data from your tank monitor

### Propane Price Not Showing

1. Verify the pricing URL is correct for your state
2. Check that the URL loads in your web browser
3. The EIA website may be temporarily unavailable
4. Price updates once per day, so it may take 24 hours for the first reading

## Update Frequency

- **Tank levels:** Updates every 24 hours (1440 minutes)
- **Propane prices:** Updates every 24 hours (when configured)

This update schedule is designed to minimize API calls while providing timely information. The Otodata tank monitors themselves typically report data every 6-24 hours depending on the model and settings.

## Support

- **Issues & Feature Requests:** [GitHub Issues](https://github.com/briadelour/otodata-tank-monitor/issues)
- **Otodata Support:** Contact Otodata for issues with your tank monitoring hardware or account
- **Home Assistant Community:** [Home Assistant Forums](https://community.home-assistant.io/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This integration is provided as-is for personal use. Otodata and its API are property of their respective owners.

## Disclaimer

This is an unofficial integration and is not affiliated with, endorsed by, or connected to Otodata or Otodata Network. Use at your own risk. Always maintain multiple methods of monitoring critical systems like propane levels.

---

Made with ❤️ for the Home Assistant community
