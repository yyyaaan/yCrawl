from . config import *
from . url_builder import url_hotel, url_qr
from google.cloud import storage
from datetime import date
from random import shuffle


def get_keys_status(type=RUN_MODE):

    # LOCAL files_in_storage = [x for x in listdir(cache_folder) if x.endswith(".pp")]
    gcp_client = storage.Client()
    bucket = gcp_client.get_bucket("ycrawl-data")
    files_in_storage = [x.name for x in bucket.list_blobs(
        prefix=f'{RUN_MODE}/{date.today().strftime("%Y/%m/%d")}')]

    keys_completed = [
        DATE_STR + "_" + x.split("_")[1] for x in files_in_storage if not x.endswith("ERR.pp")]
    # error keys may have duplicates, LIMIT_RETRY to remove it
    keys_error = [DATE_STR + "_" + x.split("_")[1]
                  for x in files_in_storage if x.endswith("ERR.pp")]
    keys_forfeit = [
        x for x in keys_error if keys_error.count(x) >= LIMIT_RETRY]
    keys_forfeit = list(dict.fromkeys(keys_forfeit))  # remove dup

    return keys_completed, keys_forfeit, keys_error


def assign_seq(identifier):
    global NN
    NN += 1
    return f"{DATE_STR}_{identifier}{NN:04}"


def fetch_all_urls(shuffled=True):
    global NN
    NN = 0
    urls_hotel = [{
        "key": assign_seq("H"),
        "url": url_hotel(the_date, int(the_n_h.split(",")[0]), the_n_h.split(",")[1])
    }
        for the_date in HOTEL_CONFIG["checkin-list"]
        for the_n_h in HOTEL_CONFIG["hotel-nights"]
    ]

    NN = 0
    urls_qr = [{
        "key": assign_seq("Q"),
        "url": url_qr(a, b, c, d, x, QR_CONFIG["center-days"])
    }
        for a in QR_CONFIG["origins"].split(",")
        for b in QR_CONFIG["destinations"].split(",")
        for c in QR_CONFIG["destinations"].split(",")
        for d in QR_CONFIG["origins"].split(",")
        for x in QR_CONFIG["dep-date-list"]
    ]

    all_urls = urls_hotel + urls_qr
    if shuffled:
        shuffle(all_urls)

    return all_urls


def call_coordinator():
    urls_all = fetch_all_urls()
    keys_done, keys_forfeit, keys_error = get_keys_status(RUN_MODE)

    urls_todo = [x for x in urls_all if x['key']
                 not in (keys_done + keys_forfeit)]
    #print(f"Planned={len(urls_all)}, Completion={len(keys_done)}, Error={len(keys_forfeit)}, Todo={len(urls_todo)}")

    bash_nodes = [
        f'node node_handler.js {x["key"]} "' + x['url'] + '"' for x in urls_todo]

    return "\n".join(bash_nodes)


if __name__ == "__main__":
    call_coordinator()
