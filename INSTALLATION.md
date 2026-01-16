# Installation Guide

This guide will walk you through installing and configuring the Otodata Propane Tank Monitor integration for Home Assistant.

## Prerequisites

Before you begin, ensure you have:

1. **Home Assistant** (version 2023.8.0 or later)
2. **HACS** (Home Assistant Community Store) installed
3. **A Otodata account** with registered tank monitor(s)
4. **Nee-Vo mobile app** installed and configured:
   - [iOS App](https://apps.apple.com/us/app/nee-vo/id1108454345)
   - [Android App](https://play.google.com/store/apps/details?id=ca.otodata.nee_vo&hl=en_US&pli=1)

## Step 1: Set Up Your Otodata Account

If you haven't already set up your Otodata account:

1. **Download the Nee-Vo mobile app** from the links above
2. **Create an account** or sign in to an existing one
3. **Locate your tank monitor's code**:
   - Find the alpha-numeric code on your Nee-Vo tank monitor device
   - This is typically a QR code with a code below it
4. **Register the device**:
   - In the app, tap to add a new device
   - Scan the QR code or manually enter the alpha-numeric code
   - **Important**: Register as the "home owner" 
     - You can do this even if you don't physically own the tank monitor
     - This gives you API access needed for Home Assistant
5. **Verify you can see your tank level** in the mobile app
6. **Remember your username and password** - you'll need these for Home Assistant

## Step 2: Install HACS (if not already installed)

If you don't have HACS installed:

1. Visit [HACS Installation Guide](https://hacs.xyz/docs/setup/download)
2. Follow the installation instructions
3. Restart Home Assistant
4. Configure HACS through the Home Assistant UI

## Step 3: Install the Otodata Integration via HACS

### Option A: Add as Custom Repository (until accepted into default HACS)

1. Open **HACS** in Home Assistant
2. Click on **Integrations**
3. Click the **three dots (⋮)** in the top right corner
4. Select **Custom repositories**
5. Enter the repository URL: `https://github.com/briadelour/otodata-tank-monitor`
6. Select category: **Integration**
7. Click **Add**
8. Find "Otodata Propane Tank Monitor" in the list
9. Click **Download**
10. Select the latest version
11. Click **Download**
12. **Restart Home Assistant**

### Option B: Manual Installation (alternative method)

1. Download the latest release from [GitHub Releases](https://github.com/briadelour/otodata-tank-monitor/releases)
2. Extract the ZIP file
3. Copy the `custom_components/neevo` folder to your Home Assistant `custom_components` directory
   - Path should be: `/config/custom_components/neevo/`
   - If `custom_components` doesn't exist, create it
4. **Restart Home Assistant**

## Step 4: Configure the Integration

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click the **+ Add Integration** button
3. Search for **"Otodata Propane Tank Monitor"**
4. Enter your credentials:
   - **Otodata Username**: Your Nee-Vo app username
   - **Otodata Password**: Your Nee-Vo app password
   - **Propane Pricing URL** (optional): See Step 5 below
5. Click **Submit**

The integration will validate your credentials and connect to your Otodata account.

## Step 5: Configure Propane Pricing (Optional)

To track propane prices in your area:

### Finding Your State's EIA Pricing URL

1. Visit the [EIA Weekly Residential Propane Prices page](https://www.eia.gov/dnav/pet/pet_pri_wfr_a_EPM0_PRS_dpgal_w.htm)
2. Find your state in the list
3. Click on your state name
4. Copy the URL from your browser's address bar

### Quick Reference - All Supported States

**New England:**
- Connecticut: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SCT_w.htm`
- Maine: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SME_w.htm`
- Massachusetts: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SMA_w.htm`
- New Hampshire: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SNH_w.htm`
- Rhode Island: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SRI_w.htm`
- Vermont: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SVT_w.htm`

**Mid-Atlantic:**
- Delaware: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SDE_w.htm`
- District of Columbia: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SDC_w.htm`
- Maryland: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SMD_w.htm`
- New Jersey: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SNJ_w.htm`
- New York: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SNY_w.htm`
- Pennsylvania: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SPA_w.htm`

**Southeast:**
- Florida: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SFL_w.htm`
- Georgia: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SGA_w.htm`
- North Carolina: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SNC_w.htm`
- Virginia: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SVA_w.htm`

**Midwest:**
- Illinois: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SIL_w.htm`
- Indiana: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SIN_w.htm`
- Iowa: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SIA_w.htm`
- Kansas: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SKS_w.htm`
- Kentucky: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SKY_w.htm`
- Michigan: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SMI_w.htm`
- Minnesota: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SMN_w.htm`
- Missouri: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SMO_w.htm`
- Nebraska: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SNE_w.htm`
- North Dakota: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SND_w.htm`
- Ohio: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SOH_w.htm`
- Oklahoma: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SOK_w.htm`
- South Dakota: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SSD_w.htm`
- Tennessee: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_STN_w.htm`
- Wisconsin: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SWI_w.htm`

**South:**
- Alabama: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SAL_w.htm`
- Arkansas: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SAR_w.htm`
- Mississippi: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SMS_w.htm`
- Texas: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_STX_w.htm`

**Mountain:**
- Colorado: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SCO_w.htm`
- Idaho: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SID_w.htm`
- Montana: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SMT_w.htm`
- Utah: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SUT_w.htm`

**Regional Averages:**
- US National: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_nus_w.htm`
- East Coast: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_R10_w.htm`
- Midwest: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_R20_w.htm`
- Gulf Coast: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_R30_w.htm`
- Rocky Mountain: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_R40_w.htm`

### URL Pattern

The URL follows this pattern:
```
https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_[STATE_CODE]_w.htm
```

Where `[STATE_CODE]` is typically `S` followed by the two-letter state abbreviation (e.g., `SOH` for Ohio, `SNY` for New York).

## Step 6: Verify Installation

After configuration:

1. Go to **Settings** → **Devices & Services**
2. Find **Otodata Propane Tank Monitor** in the list
3. Click on it to see your device(s)
4. You should see:
   - One **level sensor** per tank: `sensor.neevo_tank_1`, `sensor.neevo_tank_2`, etc.
   - One **gallons sensor** per tank: `sensor.neevo_tank_1_gallons_remaining`, etc.
   - One **liters sensor** per tank: `sensor.neevo_tank_1_liters_remaining`, etc.
   - One **pressure sensor** per tank (if your monitor supports it): `sensor.neevo_tank_1_pressure`, etc.
   - One **price sensor** (if configured): `sensor.propane_price`

**Note:** Tank sensors will use your custom names from the Nee-Vo app if you've set them. Pressure sensors are only created for tanks that report pressure data (some older monitors may not have this feature).

## Step 7: Add to Dashboard

Create a dashboard card to view your tank level:

1. Go to your dashboard
2. Click **Edit Dashboard**
3. Click **+ Add Card**
4. Choose **Gauge** card
5. Configure:
   - **Entity**: `sensor.neevo_tank_1`
   - **Name**: "Propane Tank"
   - **Min**: 0
   - **Max**: 100
   - Set severity thresholds (green: 50, yellow: 25, red: 0)
6. Click **Save**

## Troubleshooting

### Integration Not Found

- Ensure you've restarted Home Assistant after installation
- Check that the files are in `/config/custom_components/neevo/`
- Clear your browser cache (Ctrl+F5)

### Invalid Credentials Error

- Verify you can log in to the Nee-Vo mobile app with the same credentials
- Check for typos in username/password
- Ensure your account has active tank monitoring

### No Devices Found

- Make sure you've registered at least one tank in the Nee-Vo mobile app
- Verify you registered as the "home owner" (not just a viewer)
- Check that you can see tank data in the mobile app

### Sensors Show "Unavailable"

- Check Home Assistant logs: **Settings** → **System** → **Logs**
- Look for errors related to "neevo"
- Try reloading the integration: **Settings** → **Devices & Services** → **Otodata** → **⋮** → **Reload**

### Propane Price Not Working

- Verify the URL loads in your web browser
- Make sure you copied the complete URL including `https://`
- The EIA updates prices weekly, so new data may take up to 24 hours to appear

## Next Steps

- Set up [automations](README.md#automations) for low tank alerts
- Create additional dashboard cards
- Configure notifications

## Getting Help

- Check the [README](README.md) for detailed documentation
- Review [common issues](README.md#troubleshooting)
- Open an [issue on GitHub](https://github.com/briadelour/otodata-tank-monitor/issues)
- Ask in the [Home Assistant Community](https://community.home-assistant.io/)
