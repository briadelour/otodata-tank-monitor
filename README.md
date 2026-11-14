# Otodata Tank Monitor for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/briadelour/otodata-tank-monitor.svg)](https://github.com/briadelour/otodata-tank-monitor/releases)

Monitor your Otodata propane tank levels directly in Home Assistant. Access your tank data through the Nee-Vo portal by Otodata Network. This is a custom integration that can be installed via HACS.

<div align="center">
<img width="502" height="494" alt="Otodata Tank Monitor Screenshot" src="https://github.com/user-attachments/assets/d08153cb-b5fd-43ab-8d34-5b74f099cc57" />
</div>

## Features

- **Tank level monitoring** - Track your propane tank fill percentage and volume remaining
- **Energy dashboard support** - A cumulative `Gas Consumption` sensor that ignores deliveries (see [ENERGY_DASHBOARD.md](ENERGY_DASHBOARD.md))
- **Configurable updates** - Default every 6 hours; adjustable (15 to 1440 minutes) under the integration's **Configure** button
- **Multiple tank support** - Monitor multiple propane tanks from one account
- **Current state details** - Last reading date, tank capacity, and alert thresholds. The integration reads only the tank's current state; it does not import history from the Nee-Vo app. Home Assistant records its own history from the time you install the integration
- **Optional propane pricing** - Track EIA state-average residential propane prices (used for Energy dashboard cost)
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

1. **Home Assistant** installed and running (version 2024.11.0 or later)
2. **Otodata Tank Reader** installed and reporting (Model TM5030 used for this development)
3. **A Nee-Vo portal account** with active propane tank monitoring service
4. **The Nee-Vo mobile app** installed on your phone:
   - [iOS App](https://apps.apple.com/us/app/nee-vo/id1108454345)
   - [Android App](https://play.google.com/store/apps/details?id=ca.otodata.nee_vo&hl=en_US&pli=1)

<div align="center">
<img width="256" height="256" alt="icon" src="https://github.com/user-attachments/assets/e142e331-8e46-41b6-9d1c-69177226c0dd" />
</div>

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
2. Extract the `custom_components/otodata_tank_monitor` folder to your Home Assistant `custom_components` directory
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

> **Entity IDs depend on your tank name.** If you set a custom name in the Nee-Vo app (for example "Amerigas propane"), entity IDs are built from it (`sensor.amerigas_propane`, `sensor.amerigas_propane_gas_consumption`). With no custom name, the level sensor is `sensor.neevo_tank_1` and the others use `Tank 1` (`sensor.tank_1_gallons_remaining`, `sensor.tank_1_gas_consumption`). Examples below use the no-custom-name form; substitute your own IDs.

| Sensor | Unit | What it is | Use for |
|---|---|---|---|
| **Tank level** (`sensor.neevo_tank_1`) | % | Fill percentage of the tank's *total* capacity | Gauges, alerts |
| **Gallons Remaining** | gal | Level % × capacity | Gauges, alerts |
| **Liters Remaining** | L | Level % × capacity | Gauges (metric) |
| **Cubic Feet Remaining** | ft³ | Liquid volume remaining (informational) | Reference only |
| **Gas Consumption** | ft³ | Running total of propane used. Deliveries are ignored | **Energy dashboard** |
| **Pressure** (if reported) | PSI | Tank pressure, converted from kPa | Monitoring |
| **Propane Price** (if configured) | USD/ft³ | EIA state average × 7.48052 (see attributes for $/gal) | Energy dashboard cost |

**Energy dashboard:** use *Gas Consumption* only. The *Remaining* sensors go down as you use propane and would show negative usage. See [ENERGY_DASHBOARD.md](ENERGY_DASHBOARD.md) for setup, units, and what to expect.

**Gas Consumption details:** each time the integration polls, a drop in tank volume is added to the total and a rise (a delivery) is ignored. The total survives restarts and starts at 0 on a new install. Its `previous_volume_ft3` attribute is how it remembers the last reading, so don't edit it.

**Propane Price details:** the price is converted from EIA's $/gal. Attributes: `price_per_gallon`, and `price_is_stale` (true when EIA has no fresh value and the last good price is being reused, which can happen outside the October-March weekly reporting season).

### Sensor Attributes

Each tank level sensor provides these attributes:

**Basic Information:**
- **level** - Current tank fill percentage
- **tank_capacity** / **tank_capacity_liters** - Total capacity as reported by the API, in **liters** (1211.2 for a 320 gal tank)
- **tank_capacity_gallons** - Total capacity in gallons (use this one in templates)
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
- **propane_price** - Latest EIA residential propane price in $/gal (raw value from the EIA page)

### Dashboard Examples

#### Gauge Card

```yaml
type: gauge
entity: sensor.neevo_tank_1
unit: "%"
segments:
  - from: 0
    color: "#db4437"
  - from: 20
    color: "#ffa600"
  - from: 30
    color: "#43a047"
  - from: 80
    color: "#d3d3d3"
needle: true
max: 80
name: Propane Tank (320gal)
```

#### Enchanced Mushroom Card (requires [Mushroom Template](https://github.com/piitaya/lovelace-mushroom/blob/main/docs/cards/template.md))

```yaml
type: custom:mushroom-template-card
primary: Propane Tank
secondary: >-
  {{ states("sensor.neevo_tank_1") }}% ({{
  states("sensor.tank_1_gallons_remaining") | float(0) | round(0) }} gal)
icon: mdi:storage-tank
color: |-
  {% set level = states('sensor.neevo_tank_1') | float %}
  {% if level > 50 %}green
  {% elif level > 30 %}orange
  {% else %}red
  {% endif %}
features_position: bottom
```

#### Entity Card

```yaml
type: entities
entities:
  - entity: sensor.neevo_tank_1
    name: Tank Level
  - entity: sensor.tank_1_gallons_remaining
    name: Gallons Remaining
  - entity: sensor.tank_1_liters_remaining
    name: Liters Remaining
  - type: attribute
    entity: sensor.neevo_tank_1
    attribute: last_reading_date
    name: Last Reading
  - type: attribute
    entity: sensor.neevo_tank_1
    attribute: tank_capacity_gallons
    name: Tank Capacity (gal)
  - entity: sensor.propane_price
    name: Current Price
```

#### Advanced Card

```yaml
type: vertical-stack
cards:
  - type: entities
    entities:
      - entity: sensor.neevo_tank_1
        secondary_info: last-changed
        name: Propane Tank Level (last changed)
      - entity: sensor.tank_1_gallons_remaining
        secondary_info: last-changed
      - entity: sensor.tank_1_liters_remaining
      - entity: sensor.propane_price
        secondary_info: last-changed
      - entity: update.otodata_tank_monitor_update
        secondary_info: none
  - type: button
    tap_action:
      action: call-service
      service: homeassistant.reload_config_entry
      service_data:
        entry_id: {uuid string}
    name: Reload Integration
    icon: mdi:refresh
    card_mod:
      style: |
        ha-card {
          height: 32px !important;
          min-height: 32px !important;
        }
```
NOTE: Go to Developer Tools and run homeassistant.reload_config_entry to find the UUID string for update.otodata_tank_monitor_update.

## Energy Dashboard

Add **Gas Consumption** as the gas source and **Propane Price** (or a static price) for cost. Full guide, including units, limitations for refilled tanks, and troubleshooting: [ENERGY_DASHBOARD.md](ENERGY_DASHBOARD.md).

## Upgrading from 1.x to 2.0.0

Version 2.0.0 requires Home Assistant 2024.11.0 or later. See the [CHANGELOG](CHANGELOG.md) for everything that changed. The ones that may affect you:

- **Liters / Cubic Feet / Gallons Remaining** changed device class (to volume storage) and state class (to measurement), so they no longer appear in the Energy dashboard picker. Home Assistant may show a statistics warning for them: go to **Developer Tools** → **Statistics** and use **Fix issue**, choosing to delete the old statistics. If you had one of these selected as your Energy gas source, switch to **Gas Consumption**.
- **Liters Remaining** now shows liters. Before, Home Assistant displayed it in ft³ for US unit systems.
- **Update interval** default is now 6 hours (it was a fixed 24 hours). Existing installs pick this up automatically; change it under **Configure** if you prefer a different value.
- **Propane Price** unit is unchanged (USD/ft³). The price is now kept through EIA gaps instead of becoming `unknown`.
- Entity IDs and unique IDs are unchanged.

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
            Current propane price: ${{ state_attr('sensor.propane_price', 'price_per_gallon') }}/gal
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

- The sensor updates every 6 hours by default. Change this under **Settings** → **Devices & Services** → **Otodata Tank Monitor** → **Configure** (15 to 1440 minutes)
- You can force an update by reloading the integration: **Settings** → **Devices & Services** → **Otodata** → **⋮** → **Reload**
- Check the `last_reading_date` attribute to see when Otodata last received data from your tank monitor

### Propane Price Not Showing

1. Verify the pricing URL is correct for your state
2. Check that the URL loads in your web browser
3. The EIA website may be temporarily unavailable
4. EIA reports propane weekly from October through March and monthly the rest of the year, and some periods have no value. The integration keeps the last good price and sets `price_is_stale: true` on the sensor
5. A fresh install needs one successful poll before a price appears
6. For exact costs, skip the EIA price and use a static price in the Energy dashboard (your price per gallon × 7.48 = price per ft³)

## Update Frequency

- **Tank levels and prices:** every 6 hours (360 minutes) by default, adjustable from 15 to 1440 minutes under **Configure**. The schedule starts when Home Assistant starts or the integration is reloaded.

The Otodata tank monitors themselves typically report every 6-24 hours depending on model and settings, so polling much faster than hourly rarely helps. The longest a reading can lag is roughly the device's report interval plus your update interval. Energy dashboard usage is stamped with the time the integration *polled*, not the time the propane was burned.

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
