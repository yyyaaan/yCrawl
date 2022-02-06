from datetime import datetime

# 4-day runing shedule controller
controller = (
    (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) \
     - datetime(1970,1,1)) \
    .days) % 4

print(controller)
