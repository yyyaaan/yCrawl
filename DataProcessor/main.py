# %%
from google.cloud import storage #, bigquery
from bs4 import BeautifulSoup
from tqdm import tqdm
from pandas import DataFrame
from datetime import date, datetime
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

ALL_FILES = [x.name for x in GS_STAGING.list_blobs(prefix=f'{RUN_MODE}/{date.today().strftime("%Y%m/%d")}')]
ALL_FILES = [x for x in ALL_FILES if x.endswith(".pp")]

GS_ARCHIVE = GS_CLIENT.get_bucket("ycrawl-data")
BIG_THRESHOLD, BIG_N, BIG_STR = 300, 0, ""
SEP_STR = "<!--NEW FILE--->"


GS_OUTPUT = GS_CLIENT.get_bucket("ycrawl-data")

# %%
# save BIG_STR to achive
def save_big_str(one_str):
    global BIG_THRESHOLD, BIG_N, BIG_STR
    BIG_STR += SEP_STR + one_str
    BIG_N +=1

    if one_str=="END" or BIG_N > BIG_THRESHOLD:
        blob = GS_ARCHIVE.blob(f'BIGSTR/{datetime.now().strftime("%Y%m/BIG_%H%M%S")}.txt')
        blob.upload_from_string(BIG_STR)
        BIG_N, BIG_STR = 0, ""

    return True

# %%
# debug code
from random import choices
ALL_FILES = choices(ALL_FILES, k=100) 


MSG, list_errs, list_flights, list_hotels = "", [],[],[]

for one_filename in tqdm(ALL_FILES):
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
        MSG += f"\nVendor not found {vendor}"

print(MSG)
save_big_str("END")

# %%



# %%
df_errs = DataFrame(list_errs)
df_flights = DataFrame(list_flights)
df_hotels = DataFrame(list_hotels)


# %%
df_hotels

#%%
import pyarrow
df_hotels.to_parquet('./cache/df_hotels.parquet.gzip', compression='gzip')  


# pd.read_parquet('df.parquet.gzip') 
# %%
