# Otodata Tank Monitor

Monitor your Otodata propane tank levels directly in Home Assistant. Access your tank data through the Nee-Vo portal by Otodata Network.

## Features

✅ Real-time tank level monitoring  
✅ Volume sensors (gallons & liters)  
✅ Multiple tank support  
✅ Optional propane price tracking  
✅ Tank pressure sensors (automatic kPa to PSI conversion)  
✅ Easy UI configuration  
✅ Automatic daily updates  

## Quick Setup

1. Install via HACS
2. Add integration through UI
3. Enter your Nee-Vo portal credentials
4. Optionally add propane pricing URL

## Requirements

- Active Otodata tank monitor
- Nee-Vo portal account ([iOS](https://apps.apple.com/us/app/nee-vo/id1108454345) | [Android](https://play.google.com/store/apps/details?id=ca.otodata.nee_vo&hl=en_US&pli=1))
- Tank monitor registered as home owner

## Propane Pricing

Track local propane prices by adding your state's EIA URL:

- **North Carolina**: https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_snc_w.htm
- **Connecticut**: https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SCT_w.htm
- **Ohio**: https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SOH_w.htm

Find your state: https://www.eia.gov/dnav/pet/pet_pri_wfr_a_EPM0_PRS_dpgal_w.htm

---

**Note:** Otodata tank monitors are accessed through the Nee-Vo portal. This is an unofficial integration.
