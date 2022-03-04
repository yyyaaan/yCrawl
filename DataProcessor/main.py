# %%
from distutils.command.upload import upload
from os import system
from sys import argv
from bs4 import BeautifulSoup
from json import dumps, loads
from random import shuffle
from pandas import DataFrame, concat
from requests import get, post
from datetime import datetime
from google.cloud import storage

from cooker import *
from reporting import *


####################################################################################
### TO BE USED in current directory, not called from elsewhere #####################
########################################################## global vars in __main__ #


TESTTEST = int(argv[2]) if len(argv) > 2 and argv[1] == "test" else 0
UPLOAD = True if TESTTEST in [0, 9999] else False

META = loads(get("https://raw.githubusercontent.com/yyyaaan/metadata/main/ycrawl.json").text)
RUN_MODE = META["scope"]
GS_CLIENT = storage.Client(project="yyyaaannn")
GS_STAGING = GS_CLIENT.get_bucket(META["bucket"])
GS_OUTPUTS = GS_CLIENT.get_bucket(META["bucket-outputs"])
GS_ARCHIVE = GS_CLIENT.get_bucket(META["bucket-archive"])
TAG_Ym, TAG_Ymd, TAG_d = datetime.now().strftime("%Y%m/"), datetime.now().strftime("%Y%m%d"), datetime.now().strftime("%d")

ALL_FILES = [x.name for x in GS_STAGING.list_blobs(prefix=f"{RUN_MODE}/{TAG_Ym}{TAG_d}")]
ALL_FILES = [x for x in ALL_FILES if x.endswith(".pp")]
shuffle(ALL_FILES)

if TESTTEST > 0:
    from random import choices
    if TESTTEST < len(ALL_FILES):
        ALL_FILES = choices(ALL_FILES, k=TESTTEST)


# %% periodically save pulled source to archive -> NOT multi-process safe
BIG_THRESHOLD, BIG_N, PART_N, BIG_STR = 200, 0, 1, ""

def save_big_str(one_str):
    global BIG_THRESHOLD, BIG_N, BIG_STR, PART_N, SEP_STR
    BIG_STR += "<!--NEW FILE--->" + str(one_str)
    BIG_N +=1

    if one_str=="END" or BIG_N > BIG_THRESHOLD:
        blob = GS_ARCHIVE.blob(f'BIGSTR/{TAG_Ym}{TAG_Ymd}_BIG{PART_N:02}.txt')
        blob.upload_from_string(BIG_STR)
        BIG_N, BIG_STR = 0, ""
        PART_N +=1

    return True


# %% multi-processing module  -> currently only use one
def assemble_dataframe(file_list):

    ## first, iterate all files
    list_errs, list_flights, list_hotels, files_exception = [],[],[],[]
    if TESTTEST > 0:
        from tqdm import tqdm
        file_list = tqdm(file_list)

    for one_filename in file_list:
        try:
            one_str = GS_STAGING.get_blob(one_filename).download_as_string()
            save_big_str(one_str)
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
            continue

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
 

    # second, create dataframe according to data
    hotels_by_room, hotels_by_rate, hotels_failed = [], [], []
    for x in list_hotels:
        if len(x["room_type"]) == len(x["rate_sum"]) and len(x["rate_sum"]) == len(x["rate_avg"]):
            hotels_by_room.append(x)
        elif len(x["rate_type"]) == len(x["rate_sum"]) and len(x["rate_sum"]) == len(x["rate_avg"]):
            hotels_by_rate.append(x)
        else:
            hotels_failed.append(x)

    df_hotels_1 = DataFrame(hotels_by_rate).explode(["rate_type", "rate_sum", "rate_avg"]) if len(hotels_by_rate) else None
    df_hotels_2 = DataFrame(hotels_by_room).explode(["room_type", "rate_sum", "rate_avg"]) if len(hotels_by_room) else None

    df_hotels = concat([df_hotels_1, df_hotels_2])
    df_flights = DataFrame(list_flights)
    df_errs = DataFrame(list_errs)

    return df_hotels, df_flights, df_errs, hotels_failed, files_exception



# %%
def main():    
    if TESTTEST == 0 or (len([x.name for x in GS_OUTPUTS.list_blobs(prefix=f"yCrawl_Output/{TAG_Ym}{TAG_Ymd}")]) > 1):
        print("DataProcessor Step has been completed for today. No action for this request")
        return True

    df_hotels, df_flights, df_errs, hotels_failed, files_exception = assemble_dataframe(ALL_FILES)

    ecb = get_ecb_rate()
    df_errs = finalize_df_errs(df_errs, files_exception, upload=UPLOAD)
    df_flights_final = finalize_df_flights(df_flights, ecb, upload=UPLOAD)
    df_hotels_final = finalize_df_hotels(df_hotels, ecb, upload=UPLOAD)

    if UPLOAD:
        # raw results output
        df_hotels.to_parquet(f"{TAG_Ymd}_hotels.parquet.gzip", compression='gzip')
        df_flights.to_parquet(f"{TAG_Ymd}_flights.parquet.gzip", compression='gzip')
        system(f"gsutil mv *.gzip gs://{str(GS_OUTPUTS.name)}/yCrawl_Output/{TAG_Ym}/")

        # send line message for summary, AUTHKEY system registered
        prepare_flex_msg(df_flights_final, df_hotels_final, msg_endpoint=META["MSG_ENDPOINT"])

        # copy of saved metadata
        system(f"gsutil cp gs://staging.yyyaaannn.appspot.com/prod1/{TAG_Ym}{TAG_d}/0_meta_on_completion.json gs://yyyaaannn-us/yCrawl_Output/{TAG_Ym}{TAG_Ymd}_meta.json")

        # move erroreouns files
        errfiles = [f"gs://{str(GS_STAGING.name)}/{x}" for x in [y['filename'] for y in files_exception if "sold out" not in y["errm"]]]
        if len(errfiles):
            with open("tmplist", "w") as f:
                f.write("\n".join(errfiles))
            system(f"cat tmplist | gsutil -m cp -I gs://{str(GS_OUTPUTS.name)}/yCrawl_Review/{TAG_Ym}{TAG_d}/")
        if len(hotels_failed):
            (GS_OUTPUTS
                .blob(f"yCrawl_Review/{TAG_Ym}{TAG_d}/hotels_parse_issue.json")
                .upload_from_string(dumps(hotels_failed, indent=4, default=str))
            )

    return True


if __name__ == "__main__":
    print(f"\n========= START {datetime.now().strftime('%Y-%m-%dT%X')} =========")
    main()
    print(f"\nDONE {datetime.now().strftime('%Y-%m-%dT%X')}")
    res = post(META["DATA_ENDPOINT"], json = {"STOP": "done", "VMID": getenv("VMID"), "AUTH": getenv("AUTHKEY")})
    print(f"shutdown notice {res.status_code} {res.text}\n")


