"""Constants for the Otodata Tank Monitor integration."""

DOMAIN = "otodata_tank_monitor"

# Configuration
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_PRICING_URL = "pricing_url"
# Options (set from the integration's "Configure" button)
CONF_SCAN_INTERVAL = "scan_interval"  # minutes
CONF_SPIKE_THRESHOLD = "spike_threshold"  # percent of tank capacity

# API
API_URL = "https://ws.otodatanetwork.com/neevoapp/v1/DataService.svc/GetAllDisplayPropaneDevices"
API_TIMEOUT = 30

# Defaults
DEFAULT_SCAN_INTERVAL = 360  # 6 hours in minutes
MIN_SCAN_INTERVAL = 15  # minutes
MAX_SCAN_INTERVAL = 1440  # minutes
# A single-reading drop larger than this (percent of tank capacity) is held
# until a second, different reading confirms it. 0 turns the protection off.
DEFAULT_SPIKE_THRESHOLD = 10
MIN_SPIKE_THRESHOLD = 0
MAX_SPIKE_THRESHOLD = 50
# A level rise of at least this many percentage points is treated as a delivery.
DELIVERY_MIN_PERCENT = 5

# Event fired when a delivery (fill) is detected
EVENT_TANK_FILLED = "otodata_tank_monitor_tank_filled"
DEFAULT_NAME = "Otodata Tank"

# Conversion factors
KPA_TO_PSI = 0.145038  # 1 kPa = 0.145038 PSI
GALLONS_TO_LITERS = 3.78541  # 1 gallon = 3.78541 liters
LITERS_TO_CUBIC_FEET = 0.0353147  # liquid volume, not gas vapor volume
GALLONS_TO_CUBIC_FEET = 0.133681  # 1 gallon = 0.133681 ft³ (7.48052 gal per ft³)
CUBIC_FEET_TO_GALLONS = 7.48052

# State URLs by state (complete list from EIA)
STATE_PRICING_URLS = {
    "US": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_nus_w.htm",
    # East Coast (PADD 1)
    "PADD1": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_R10_w.htm",
    # New England (PADD 1A)
    "PADD1A": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_R1X_w.htm",
    "CT": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SCT_w.htm",
    "ME": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SME_w.htm",
    "MA": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SMA_w.htm",
    "NH": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SNH_w.htm",
    "RI": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SRI_w.htm",
    "VT": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SVT_w.htm",
    # Central Atlantic (PADD 1B)
    "PADD1B": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_R1Y_w.htm",
    "DE": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SDE_w.htm",
    "DC": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SDC_w.htm",
    "MD": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SMD_w.htm",
    "NJ": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SNJ_w.htm",
    "NY": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SNY_w.htm",
    "PA": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SPA_w.htm",
    # Lower Atlantic (PADD 1C)
    "PADD1C": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_R1Z_w.htm",
    "FL": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SFL_w.htm",
    "GA": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SGA_w.htm",
    "NC": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SNC_w.htm",
    "VA": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SVA_w.htm",
    # Midwest (PADD 2)
    "PADD2": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_R20_w.htm",
    "IL": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SIL_w.htm",
    "IN": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SIN_w.htm",
    "IA": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SIA_w.htm",
    "KS": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SKS_w.htm",
    "KY": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SKY_w.htm",
    "MI": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SMI_w.htm",
    "MN": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SMN_w.htm",
    "MO": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SMO_w.htm",
    "NE": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SNE_w.htm",
    "ND": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SND_w.htm",
    "OH": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SOH_w.htm",
    "OK": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SOK_w.htm",
    "SD": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SSD_w.htm",
    "TN": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_STN_w.htm",
    "WI": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SWI_w.htm",
    # Gulf Coast (PADD 3)
    "PADD3": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_R30_w.htm",
    "AL": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SAL_w.htm",
    "AR": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SAR_w.htm",
    "MS": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SMS_w.htm",
    "TX": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_STX_w.htm",
    # Rocky Mountain (PADD 4)
    "PADD4": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_R40_w.htm",
    "CO": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SCO_w.htm",
    "ID": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SID_w.htm",
    "MT": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SMT_w.htm",
    "UT": "https://www.eia.gov/dnav/pet/pet_pri_wfr_dcus_SUT_w.htm",
}

# Attributes
ATTR_LEVEL = "level"
ATTR_LAST_READING = "last_reading_date"
ATTR_TANK_CAPACITY = "tank_capacity"
ATTR_PROPANE_PRICE = "propane_price"
ATTR_SERIAL_NUMBER = "serial_number"
ATTR_CUSTOM_NAME = "custom_name"
ATTR_COMPANY_NAME = "company_name"
ATTR_NOTIFY_AT_1 = "notify_at_level_1"
ATTR_NOTIFY_AT_2 = "notify_at_level_2"
ATTR_TANK_PRESSURE = "tank_pressure"
ATTR_PRESSURE_UNIT = "pressure_unit"
ATTR_IS_OWNER = "is_owner"
ATTR_PRODUCT = "product"
