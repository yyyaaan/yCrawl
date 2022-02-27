from config import *
from datetime import datetime
from google.cloud import logging, storage
from Coordinator.main import fetch_all_urls

def storage_file_viewer(run_mode=RUN_MODE):

    bucket = storage.Client().get_bucket(GSBUCKET)
    all_files = [x.name for x in bucket.list_blobs(prefix=f'{run_mode}/{datetime.now().strftime("%Y%m/%d")}')]
    info_str = "All scheduled tasks done." if len([x for x in all_files if "meta_on_completion" in x]) else "In progress..."
        
    all_uurls = fetch_all_urls()
    uurls_by_key = dict([(x['key'].split("_")[1], x['url']) for x in all_uurls])

    revert_batch = dict([(x['batch'], x['name']) for x in META['cluster']])

    main_list_draft = [{
        "key": the_key,
        "batchn": int(the_key[1:]) % len(revert_batch),
        "link": [f'https://storage.cloud.google.com/{GSBUCKET}/{x}' for x in all_files if f"_{the_key}_" in x],
        "uurl": uurls_by_key[the_key]
    } for the_key in [x['key'].split("_")[1] for x in all_uurls] ]

    count_err_ok = lambda lst: f"{len([y for y in lst if 'ERR' not in y])}OK{len([y for y in lst if 'ERR' in y])}E"

    main_list = [{
        "key": x["key"],
        "server": revert_batch[x["batchn"]],
        "brand": x["uurl"].split(".")[1].upper(),
        "desc": count_err_ok(x["link"]).replace("0E", "").replace("1OK","OK").replace("0OK", ""),
        "link": x["link"],
        "uurl": x["uurl"]
    } for x in main_list_draft]

    unique_brands = set([x['brand'] for x in main_list])

    output_list = [{
        "brand": the_brand,
        "list": [x for x in main_list if x['brand'] == the_brand]
    } for the_brand in sorted(list(unique_brands))]
    
    # sort has to be done in for
    for x in output_list:
        x["len"] = f"{len([y for y in x['list'] if 'OK' in y['desc']])} of {len(x['list'])}"
        x["list"].sort(key=lambda x: x["desc"] + x["key"])

    return output_list, info_str


def get_simple_log():
    log_client = logging.Client()

    the_filter = f'logName="projects/yyyaaannn/logs/stdout" AND timestamp>="{TODAY_0}"'
    log_entries = log_client.list_entries(filter_=the_filter, order_by=logging.DESCENDING)
    logs_stdout = [f'{x.timestamp.strftime("%H:%M:%S")} {x.payload}' for x in log_entries]

    ### logs orginized by server
    the_filter = f'logName="projects/yyyaaannn/logs/y_simple_log" AND timestamp>="{TODAY_0}"'
    log_entries = log_client.list_entries(filter_=the_filter, order_by=logging.DESCENDING)
    log_simplified = [f'{x.timestamp.strftime("%H:%M:%S")}{x.payload}' for x in log_entries if not str(x.payload).startswith("test")]

    logs_by_vm = [{"name": "App-Engine", "logs": "<br/>".join(logs_stdout)}]
    for the_vm in list(BATCH_REF.keys()):
        the_log_entries = [x.replace(the_vm, "") for x in log_simplified + logs_stdout if the_vm in x and "VM Manager" not in x]
        the_log = {
            "name": the_vm,
            "logs": "<br/>".join(sorted(the_log_entries, reverse=True))
        }
        logs_by_vm.append(the_log)

    return  logs_by_vm

