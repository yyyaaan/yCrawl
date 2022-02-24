from config import *
from json import dumps
from datetime import datetime
from google.cloud import logging, storage, secretmanager


GSM_CLIENT = secretmanager.SecretManagerServiceClient()
GS_CLIENT_BUCKET = storage.Client().get_bucket(GSBUCKET)

def on_all_completed(run_mode=RUN_MODE):
    blob = GS_CLIENT_BUCKET.blob(f'{run_mode}/{datetime.now().strftime("%Y%m/%d")}/0_meta_on_completion.json')
    blob.upload_from_string(dumps(META, indent=4))
    print(f"Finalized crawlers job - metadata saved")
    return True


def done_for_today(run_mode=RUN_MODE):
    all_files = [x.name for x in GS_CLIENT_BUCKET.list_blobs(prefix=f'{run_mode}/{datetime.now().strftime("%Y%m/%d")}')]
    return (len([x for x in all_files if "meta_on_completion" in x]) > 0)


def prepare_on_a_new_day():
    blob = GS_CLIENT_BUCKET.blob(f'meta/meta_{datetime.now().strftime("%Y%m%d")}.json')
    blob.upload_from_string(dumps(META, indent=4))
    return True


def determine_all_completed(caller, servers_required):
    log_client = logging.Client()
    the_filter = f'logName="projects/yyyaaannn/logs/stdout" AND timestamp>="{TODAY_0}"'
    log_text = [x.payload for x in log_client.list_entries(filter_=the_filter, order_by=logging.DESCENDING)]

    servers_completed = [x.split(" ")[-1] for x in log_text if x.startswith("Completion noted")]
    servers_completed_unique = list(set(servers_completed)) if caller is None else list(set(servers_completed + [caller]))

    flag_once = sorted(servers_required) == sorted(servers_completed_unique)
    if not flag_once:
        return False
    
    # wait for no action remaining during checkin, no message available during early checkin
    vm_manager_keyword = "VM Manager: no action "
    vm_manager_logs = [x.replace(vm_manager_keyword, "") for x in log_text if x.startswith(vm_manager_keyword)]
    latest_vm_manager = vm_manager_logs[0] if len(vm_manager_logs) else "NA NA"
    servers_all_done = [x.split("/")[0] for x in latest_vm_manager.split(" ")]

    if sorted(servers_required) == sorted(servers_all_done):
        print("All crawlers have no pending jobs. Call workflow.") 
        return True    
    if flag_once:
        print("All crawlers have completed once; remote retry in progress.")

    return False


def verify_cloud_auth(payload, keyname="ycrawl-simple-auth"):
    if payload is None or "AUTH" not in payload.keys() or payload["AUTH"] is None:
        print("AUTH: missing authentication header")
        return False

    name = f"projects/yyyaaannn/secrets/{keyname}/versions/latest"
    response = GSM_CLIENT.access_secret_version(request={"name": name})
    secretkey = response.payload.data.decode("UTF-8")
    flag = secretkey.strip() == payload["AUTH"].strip()
    if not flag: 
        print("AUTH: access denied due - wrong key")
    return flag


def get_secret(keyname="ycrawl-keep-alive"):
    name = f"projects/yyyaaannn/secrets/{keyname}/versions/latest"
    response = GSM_CLIENT.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

