from config import *
from Frontend.monitor import storage_file_viewer
from json import dumps
from requests import post
from datetime import datetime
from google.cloud import logging, storage, secretmanager

DATA_ENDPOINT = META['DATA_ENDPOINT']
GSM_CLIENT = secretmanager.SecretManagerServiceClient()
GS_CLIENT_BUCKET = storage.Client().get_bucket(GSBUCKET)

def get_secret(keyname="ycrawl-keep-alive"):
    name = f"projects/yyyaaannn/secrets/{keyname}/versions/latest"
    response = GSM_CLIENT.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def on_all_completed(run_mode=RUN_MODE):
    blob = GS_CLIENT_BUCKET.blob(f'{run_mode}/{datetime.now().strftime("%Y%m/%d")}/0_meta_on_completion.json')
    list_to_save, info_str = storage_file_viewer()
    json_to_save = META
    json_to_save['file-completed'] = list_to_save
    blob.upload_from_string(dumps(json_to_save, indent=4, default=str))
    try:
        post(DATA_ENDPOINT, json = {"AUTH": get_secret("ycrawl-simple-auth")})
    except Exception as e:
        print("On all completed encounted erro: " + str(e))

    print(f"Finalized crawlers job - metadata saved and data endpoint requested.")
    return True


def done_for_today(run_mode=RUN_MODE):
    all_files = [x.name for x in GS_CLIENT_BUCKET.list_blobs(prefix=f'{run_mode}/{datetime.now().strftime("%Y%m/%d")}')]
    return (len([x for x in all_files if "meta_on_completion" in x]) > 0)


def determine_all_completed(caller, servers_required):
    global DATE_STR #ensure refresh on new day
    DATE_STR = date.today().strftime("%Y%m%d")

    log_client = logging.Client()
    the_filter = f'logName="projects/yyyaaannn/logs/stdout" AND timestamp>=f"{DATE_STR}T00:00:00.123456z"'
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
        print("AUTH: access denied - wrong key")
    return flag

