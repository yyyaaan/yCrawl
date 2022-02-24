from json import loads
from requests import get
from datetime import date, timedelta


# load in the meta.json from github raw (same source as root)
live_meta = get("https://raw.githubusercontent.com/yyyaaan/metadata/main/ycrawl.json")
META = loads(live_meta.text)

GSBUCKET = META['bucket']

# Cluster control
BATCH_REF = dict([(x['name'], x['batch']) for x in META['cluster']])

# control_id is either 1, 2, 3 or 0 defines a quarter of all tasks
DATE_STR = date.today().strftime("%Y%m%d")
TODAY_0 = date.today().strftime("%Y-%m-%d") + "T00:00:00.123456z"
CONTROL_ID = ((date.today() - date(1970,1,1)).days) % 4

# mainly for coordinator
LIMIT_RETRY = META['max-retry']
RUN_MODE = META['scope']
META_URL = META['meta-url']
META_IATA = META['meta-iata']

# compute range of check in dates
range_width = int((META['date-range-max'] - META['date-range-min']) / 4)
date_adjusted_min = META['date-range-min'] - CONTROL_ID
range_delta_days = [date_adjusted_min + CONTROL_ID * range_width + x for x in range(range_width)]
HOTEL_CONFIG = META['active-hotel-config']
HOTEL_CONFIG["checkin-list"] = [date.today() + timedelta(days=x) for x in range_delta_days]

# compute qatar depature days
interval_7 = range(min(range_delta_days), max(range_delta_days), 7)
QR_CONFIG = META['active-qr-config']
QR_CONFIG["dep-date-list"] = [date.today() + timedelta(days=x) for x in interval_7]
