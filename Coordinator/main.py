from url_builder import url_hotel, url_qr
from config import *
from datetime import datetime
from random import shuffle


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



all_urls = fetch_all_urls()


bash_nodes = ['node node_handler.js "' + x['key']+ '" "' + x['url'] + '"' for x in all_urls]

print("\n".join(bash_nodes))