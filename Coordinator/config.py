from json import load
from os.path import exists
from datetime import date, timedelta


global CONTROL_ID
global DATE_STR
global META_URL
global META_IATA
global HOTEL_CONFIG
global QATAR_CONFIG

global ALL_SETTINGS

# control_id is either 1, 2, 3 or 0 defines a quarter of all tasks
DATE_STR = date.today().strftime("%Y%m%d")
CONTROL_ID = ((date.today() - date(1970,1,1)).days) % 4

# load in the meta.json
meta_path = 'meta.json' if exists('meta.json') else './Coordinator/meta.json'
with open(meta_path, 'r') as f:
    ALL_SETTINGS = load(f)

# defines hotel url code
META_URL = ALL_SETTINGS['meta-url']
META_IATA = ALL_SETTINGS['meta-iata']

# compute range of check in dates
range_width = int((ALL_SETTINGS['date-range-max'] - ALL_SETTINGS['date-range-min']) / 4)
date_adjusted_min = ALL_SETTINGS['date-range-min'] - CONTROL_ID
range_delta_days = [date_adjusted_min + CONTROL_ID * range_width + x for x in range(range_width)]
HOTEL_CONFIG = ALL_SETTINGS['active-hotel-config']
HOTEL_CONFIG["checkin-list"] = [date.today() + timedelta(days=x) for x in range_delta_days]

# compute qatar depature days
interval_7 = range(min(range_delta_days), max(range_delta_days), 7)
QR_CONFIG = ALL_SETTINGS['active-qr-config']
QR_CONFIG["dep-date-list"] = [date.today() + timedelta(days=x) for x in interval_7]