# %%
from os import system
from sys import argv
from bs4 import BeautifulSoup
from json import dumps
from random import shuffle
from pandas import DataFrame, concat
from datetime import datetime
from google.cloud import storage

from cooker import *
from reporting import *

TESTTEST = int(argv[2]) if len(argv) > 2 and argv[1] == "test" else 0
UPLOAD = True


####################################################################################
### TO BE USED in current directory, not called from elsewhere #####################
################################################### METADATA is NOT fetched live ###

RUN_MODE = "prod1"
GS_CLIENT = storage.Client(project="yyyaaannn")
GS_STAGING = GS_CLIENT.get_bucket("staging.yyyaaannn.appspot.com")
GS_OUTPUTS = GS_CLIENT.get_bucket("yyyaaannn-us")
GS_ARCHIVE = GS_CLIENT.get_bucket("ycrawl-cool")

TAG_Ym, TAG_Ymd, TAG_d = datetime.now().strftime("%Y%m/"), datetime.now().strftime("%Y%m%d"), datetime.now().strftime("%d")
print(f"\n========= START {TAG_Ymd} =========")

ALL_FILES = [x.name for x in GS_STAGING.list_blobs(prefix=f"{RUN_MODE}/{TAG_Ym}{TAG_d}")]
ALL_FILES = [x for x in ALL_FILES if x.endswith(".pp")]
shuffle(ALL_FILES)

if TESTTEST > 0:
    # debug mode show progres bar
    from random import choices
    from tqdm import tqdm
    if TESTTEST < len(ALL_FILES):
        ALL_FILES = tqdm(choices(ALL_FILES, k=TESTTEST))


BIG_THRESHOLD, BIG_N, PART_N, BIG_STR = 200, 0, 1, ""

def save_big_str(one_str):
    global BIG_THRESHOLD, BIG_N, BIG_STR, PART_N, SEP_STR
    BIG_STR += "<!--NEW FILE--->" + one_str
    BIG_N +=1

    if one_str=="END" or BIG_N > BIG_THRESHOLD:
        blob = GS_ARCHIVE.blob(f'BIGSTR/{TAG_Ym}{TAG_Ymd}_BIG{PART_N:02}.txt')
        blob.upload_from_string(BIG_STR)
        BIG_N, BIG_STR = 0, ""
        PART_N +=1

    return True

def save_exception_str(name, sstr):
    (GS_OUTPUTS
        .blob(f'yCrawl_Exceptions/{TAG_Ym}{TAG_Ymd}_{name}')
        .upload_from_string(sstr)
    )

def check_already_run(flag=TESTTEST):
    if flag > 0:
        return False
    return len([x.name for x in GS_OUTPUTS.list_blobs(prefix=f"yCrawl_Output/{TAG_Ym}{TAG_Ymd}")]) >= 3


# %%
def main():

    if check_already_run():
        print("DataProcessor Step has been completed for today. No action for this request")
        return()

    list_errs, list_flights, list_hotels, files_exception = [],[],[], []
    for one_filename in ALL_FILES:
        try:
            one_str = GS_STAGING.get_blob(one_filename).download_as_string()
            save_big_str(str(one_str))
            one_soup = BeautifulSoup(one_str, 'html.parser')
            if "_ERR" in one_filename:
                list_errs += cook_error(one_soup)
                continue
        except Exception as e:
            files_exception.append({
                "filename": one_filename, 
                "errm": str(e),
                "ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            })
        try:
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
            files_exception.append({
                "filename": one_filename, 
                "vmid": one_soup.vmid.string,
                "uurl": ".".join(one_soup.qurl.string.split(".")[1:]),
                "errm": str(e),
                "ts": one_soup.timestamp.string
            })

    save_big_str("END")


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


    # %% cleaning and upload, pre-process are saved as file
    df_flights.to_parquet(f"{TAG_Ymd}_flights.parquet.gzip", compression='gzip')
    df_hotels.to_parquet(f"{TAG_Ymd}_hotels.parquet.gzip", compression='gzip')
    if UPLOAD:
        system(f"gsutil mv *.gzip gs://{str(GS_OUTPUTS.name)}/yCrawl_Output/{TAG_Ym}/")
    
    ecb = get_ecb_rate()
    df_errs = finalize_df_errs(df_errs, files_exception, upload=UPLOAD)
    df_flights = finalize_df_flights(df_flights, ecb, upload=UPLOAD)
    df_hotels = finalize_df_hotels(df_hotels, ecb, upload=UPLOAD)

    # send line message for summary, AUTHKEY system registered
    if UPLOAD:
        prepare_flex_msg(df_flights, df_hotels, sendline=True)

        # move erroreouns files
        errfiles = [f"gs://{str(GS_STAGING.name)}/{x}" for x in [y['filename'] for y in files_exception if "sold out" not in y["errm"]]]
        if len(errfiles):
            with open("tmplist", "w") as f:
                f.write("\n".join(errfiles))
            system(f"cat tmplist | gsutil -m cp -I gs://{str(GS_OUTPUTS.name)}/yCrawl_Review/{TAG_Ym}{TAG_d}/")

        return True
    else:
        return df_errs, df_flights, df_hotels


if __name__ == "__main__":
    main()

