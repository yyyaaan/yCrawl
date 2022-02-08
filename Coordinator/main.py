from config import *
from url_builder import url_hotel, url_qr
from scan_completion import get_keys_status
from datetime import datetime
from random import shuffle
from os import getcwd

def assign_seq(identifier):
    global NN
    NN += 1
    return f"{DATE_STR}_{identifier}{NN:04}"


def publish_jobs(content, type=RUN_MODE):
    
    out_txt = "\n".join(content) if len(content) > 1 else content

    if type == "local":
        # local mode will save a file to parent directory
        path_self = getcwd().split("/")
        path_self.pop()
        path_self.append("published_jobs.txt")
        
        with open("/".join(path_self), "w") as f:
            f.write(out_txt)
    else:
        ######### TO BE IMPLEMENTED #########
        print(out_txt)

    return True



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


def main():
    urls_all = fetch_all_urls()
    keys_done, keys_forfeit, keys_error = get_keys_status(RUN_MODE)

    urls_todo = [x for x in urls_all if x['key'] not in (keys_done + keys_forfeit)]
    print(f"Planned={len(urls_all)}, Completion={len(keys_done)}, Error={len(keys_forfeit)}, Todo={len(urls_todo)}")
    
    bash_nodes = ['node node_handler.js "' + x['key']+ '" "' + x['url'] + '"' for x in urls_todo]
    publish_jobs(bash_nodes)


if __name__ == "__main__":
    main()