from config import *
from Frontend.monitor import storage_file_viewer
from json import dumps, loads
from requests import post
from datetime import datetime
from google.cloud import logging, storage, secretmanager

GSM_CLIENT = secretmanager.SecretManagerServiceClient()
GS_CLIENT_BUCKET = storage.Client().get_bucket(GSBUCKET)

def get_secret(keyname):
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
        res = post(
            META["VMA_ENDPOINT"],
            headers={"Authorization": f"Bearer {loads(get_secret('ycrawl-credentials'))['tokendata']}"},
            json = {"event": "START", "vmids": [META["data-processor-active"]], "info": "yCrawl Head" },    
        )
        if res.status_code != 200:
            print(f"VM action endpoint {res.status_code} {str(res.content)}")
    except Exception as e:
        print("On all completed raised error: " + str(e))

    print(f"Finalized crawlers job - metadata saved and data endpoint requested.")
    return True


def done_for_today(run_mode=RUN_MODE):
    all_files = [x.name for x in GS_CLIENT_BUCKET.list_blobs(prefix=f'{run_mode}/{datetime.now().strftime("%Y%m/%d")}')]
    return (len([x for x in all_files if "meta_on_completion" in x]) > 0)


def determine_all_completed(caller, servers_required):
    global DATE_STR #ensure refresh on new day
    DATE_STR = date.today().strftime("%Y%m%d")
    TODAY0 = f"{date.today().strftime('%Y-%m-%d')}T00:00:00.123456Z"

    log_client = logging.Client()
    the_filter = f'logName="projects/yyyaaannn/logs/stdout" AND timestamp>="{TODAY0}"'
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


def confirm_action_dataprocessor():
    TODAY3 = f"{date.today().strftime('%Y-%m-%d')}T03:00:00.123456Z"

    log_client = logging.Client()
    the_filter = f'logName="projects/yyyaaannn/logs/stdout" AND timestamp>="{TODAY3}"'
    logs_all = log_client.list_entries(filter_=the_filter, order_by=logging.DESCENDING)
    dp_start = [x.timestamp for x in logs_all if "data endpoint requested" in x.payload]

    if len(dp_start) == 0:
        return False # no action needed

    dp_elapsed = (datetime.now() - dp_start[0].replace(tzinfo=None)).total_seconds()
    return (1800 < dp_elapsed < 3600)



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

