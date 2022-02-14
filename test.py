from Coordinator.main import call_coordinator

# return info_str, len(urls_all), len(urls_todo), len(keys_done), len(keys_forfeit), len(keys_error)
tmp= call_coordinator(info_only=True, batch=1, total_batches=2)
print(tmp[0])


from os import getenv
from requests import get as urlget, post as urlpost

COORDINATOR_ENDPOINT = "https://yyyaaannn.ew.r.appspot.com/coordinator"
COMPLETION_ENDPOINT = "https://yyyaaannn.ew.r.appspot.com/notifydone"
COORDINATOR_ENDPOINT = "http://127.0.0.1:8080/coordinator"
COMPLETION_ENDPOINT = "http://127.0.0.1:8080/notifydone"


urlpost(COMPLETION_ENDPOINT, json = {"VMID": "ycrawl-1-pl", "AUTH": getenv("AUTHKEY")})