# %%
from os import system
from bs4 import BeautifulSoup
from tqdm import tqdm
from json import dumps
from pandas import DataFrame, concat
from datetime import datetime
from google.cloud import storage #, bigquery

from cooker import *

####################################################################################
#   ___           _ _       _     _             _   __  __           _       _      
#  |_ _|_ __   __| (_)_   _(_) __| |_   _  __ _| | |  \/  | ___   __| |_   _| | ___ 
#   | || '_ \ / _` | \ \ / / |/ _` | | | |/ _` | | | |\/| |/ _ \ / _` | | | | |/ _ \
#   | || | | | (_| | |\ V /| | (_| | |_| | (_| | | | |  | | (_) | (_| | |_| | |  __/
#  |___|_| |_|\__,_|_| \_/ |_|\__,_|\__,_|\__,_|_| |_|  |_|\___/ \__,_|\__,_|_|\___|
### TO BE USED in current directory, not called from elsewhere #####################
################################################### METADATA is NOT fetched live ###

RUN_MODE = "prod1"
GS_CLIENT = storage.Client(project="yyyaaannn")
GS_STAGING = GS_CLIENT.get_bucket("staging.yyyaaannn.appspot.com")
GS_OUTPUTS = GS_CLIENT.get_bucket("yyyaaannn-us")
GS_ARCHIVE = GS_CLIENT.get_bucket("ycrawl-data")
# GS_ARCHIVE = GS_CLIENT.get_bucket("ycrawl-cool")

BIG_THRESHOLD, BIG_N, PART_N, BIG_STR = 200, 0, 1, ""

TAG_SHORT = datetime.now().strftime("%Y%m/%Y%m%d") # when naming object with prefix
TAG_FULL = datetime.now().strftime("%Y%m/%d") # when using full path
TAG_Ym, TAG_Ymd = datetime.now().strftime("%Y%m/"), datetime.now().strftime("%Y%m%d")

ALL_FILES = [x.name for x in GS_STAGING.list_blobs(prefix=f"{RUN_MODE}/{TAG_FULL}")]
ALL_FILES = [x for x in ALL_FILES if x.endswith(".pp")]
from random import choices
ALL_FILES = choices(ALL_FILES, k=100) 


def save_big_str(one_str):
    global BIG_THRESHOLD, BIG_N, BIG_STR, PART_N, SEP_STR
    BIG_STR += "<!--NEW FILE--->" + one_str
    BIG_N +=1

    if one_str=="END" or BIG_N > BIG_THRESHOLD:
        blob = GS_ARCHIVE.blob(f'BIGSTR/{TAG_SHORT}_BIG{PART_N:02}.txt')
        blob.upload_from_string(BIG_STR)
        BIG_N, BIG_STR = 0, ""
        PART_N +=1

    return True


# %%
# exceptions are forwarded (excl. sold out) 
def save_exception_str(name, sstr):
    (GS_OUTPUTS
        .blob(f'yCrawl_Exceptions/{TAG_SHORT}_{name}')
        .upload_from_string(sstr)
    )

def check_already_run():
    return len([x.name for x in GS_OUTPUTS.list_blobs(prefix=f"yCrawl_Output/{TAG_SHORT}")]) >= 3


# %%
def main():

    if check_already_run():
        print("DataProcessor Step has been completed for today. No action for this request")
        return()

    list_errs, list_flights, list_hotels, files_exception = [],[],[], []
    for one_filename in tqdm(ALL_FILES):
        try:
            one_str = GS_STAGING.get_blob(one_filename).download_as_string()
            save_big_str(str(one_str))
            one_soup = BeautifulSoup(one_str, 'html.parser')
            if "_ERR" in one_filename:
                list_errs += cook_error(one_soup)
                continue
            vendor = one_soup.qurl.string.split(".")[1]
            if vendor == "qatarairways":
                list_flights += cook_qatar(one_soup)
            elif vendor == "marriott":
                list_hotels += cook_marriott(one_soup)
            elif vendor == "accor":
                list_hotels += cook_accor(one_soup)
            elif vendor == "hilton":
                list_hotels += cook_hilton(one_soup)
            elif vendor == "fourseasons":
                list_hotels += cook_fourseasons(one_soup)
            else:
                raise Exception(f"\nVendor not found {vendor}")

        except Exception as e:
            files_exception.append({"filename": one_filename, "exception": str(e)})

    save_big_str("END")

    # summarize exceptions
    exception_summary = [{
        "exception": x,
        "filenames": [y['filename'] for y in files_exception if y['exception'] == x]
    } for x in set([x['exception'] for x in files_exception])]
    save_exception_str(name="Exceptions.json", sstr=dumps(exception_summary, indent=4))


    # %% check hotels list-style element validity
    hotels_by_room, hotels_by_rate, hotels_failed = [], [], []
    for x in list_hotels:
        if len(x["room_type"]) == len(x["rate_sum"]) and len(x["rate_sum"]) == len(x["rate_avg"]):
            hotels_by_room.append(x)
        elif len(x["rate_type"]) == len(x["rate_sum"]) and len(x["rate_sum"]) == len(x["rate_avg"]):
            hotels_by_rate.append(x)
        else:
            hotels_failed.append(x)

    if len(hotels_failed):
        save_exception_str(name="ParseIssues.json", sstr=dumps(hotels_failed, indent=4, default=str))

    df_hotels = concat([
        DataFrame(hotels_by_rate).explode(["rate_type", "rate_sum", "rate_avg"]),
        DataFrame(hotels_by_room).explode(["room_type", "rate_sum", "rate_avg"])
    ])
    df_flights = DataFrame(list_flights)
    df_errs = DataFrame(list_errs)

    # %% file movement 
    df_flights.to_parquet(f"{TAG_Ymd}_flights.parquet.gzip", compression='gzip')
    df_hotels.to_parquet(f"{TAG_Ymd}_hotels.parquet.gzip", compression='gzip')
    df_errs.to_parquet(f"{TAG_Ymd}_errs.parquet.gzip", compression='gzip')

    system(f"gsutil mv *.gzip gs://{str(GS_OUTPUTS.name)}/yCrawl_Output/{TAG_Ym}/")

    # move erroreouns files
    errfiles = [f"gs://{str(GS_STAGING.name)}/{x}" for x in [y['filename'] for y in files_exception if "sold out" not in y["exception"]]]
    if len(errfiles):
        with open("tmplist", "w") as f:
            f.write("\n".join(errfiles))
        system(f"cat tmplist | gsutil -m cp -I gs://{str(GS_OUTPUTS.name)}/yCrawl_Review/{TAG_FULL}/")

    # source files are lifecycle controller, no need to delete

if __name__ == "__main__":
    main()

