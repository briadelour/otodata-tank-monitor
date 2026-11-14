# Quick Start Guide

Get up and running with the Otodata Propane Tank Monitor in 5 minutes!

## Prerequisites Checklist

- [ ] Home Assistant installed (2024.11.0+)
- [ ] HACS installed
- [ ] Nee-Vo mobile app installed ([iOS](https://apps.apple.com/us/app/nee-vo/id1108454345) | [Android](https://play.google.com/store/apps/details?id=ca.otodata.nee_vo&hl=en_US&pli=1))
- [ ] Otodata account created
- [ ] Tank monitor registered as home owner
- [ ] Nee-Vo username and password ready

## Installation (5 Steps)

### 1. Add to HACS (2 min)
1. Open HACS → Integrations
2. Click ⋮ → Custom repositories
3. Add: `https://github.com/briadelour/otodata-tank-monitor`
4. Category: Integration
5. Click "Download" on the Otodata card
6. Restart Home Assistant

### 2. Configure Integration (1 min)
1. Settings → Devices & Services
2. Add Integration → Search "Otodata"
3. Enter username and password
4. (Optional) Add propane pricing URL
5. Click Submit

### 3. Verify Sensors (30 sec)
1. Settings → Devices & Services → Otodata
2. Check that your tank sensor(s) appear
3. Verify they show current percentage

### 4. Add to Dashboard (1 min)
1. Dashboard → Edit
2. Add Card → Gauge
3. Entity: `sensor.neevo_tank_1`
4. Name: "Propane Tank"
5. Set min: 0, max: 100
6. Add severity levels
7. Save

### 5. Create Low Level Alert (30 sec)
1. Settings → Automations & Scenes
2. Create Automation
3. Trigger: Numeric state
4. Entity: `sensor.neevo_tank_1`
5. Below: 20
6. Action: Notify service
7. Save

## Done! 🎉

Your propane tank is now monitored in Home Assistant!

## Optional: Add Propane Pricing

Find your state's URL:
1. Visit: https://www.eia.gov/dnav/pet/pet_pri_wfr_a_EPM0_PRS_dpgal_w.htm
2. Click your state
3. Copy the URL
4. Settings → Devices & Services → Otodata → Configure
5. Add the URL

**Example URLs:**
- NC: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_snc_w.htm`
- CT: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SCT_w.htm`
- OH: `https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SOH_w.htm`

## Troubleshooting

**Integration not found?**
- Restart Home Assistant
- Clear browser cache

**Invalid credentials?**
- Test login in Nee-Vo mobile app
- Check for typos

**No devices found?**
- Verify you registered as "home owner" in app
- Check you can see tank in mobile app

## Next Steps

- [View full documentation](README.md)
- [See automation examples](EXAMPLES.md)
- [Create advanced dashboard cards](EXAMPLES.md#dashboard-examples)

## Need Help?

- [Installation Guide](INSTALLATION.md) - Detailed instructions
- [GitHub Issues](https://github.com/briadelour/otodata-tank-monitor/issues) - Report bugs
- [Home Assistant Community](https://community.home-assistant.io/) - Get support
