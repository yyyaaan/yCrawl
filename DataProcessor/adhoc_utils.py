# %% Temporary data load test
from pandas import read_parquet
from reporting import *
from cooker import *
from main import *


# %% 
def adhoc_check(GS_OUTPUTS, GS_STAGING):

    filename = "prod1/202203/08/20220308_H0497_033149764.pp"
    # filename = "prod1/202203/08/20220308_H0498_014415952.pp"
    one_str = GS_STAGING.get_blob(filename).download_as_string()
    # one_str = GS_OUTPUTS.get_blob(filename.replace("prod1", "yCrawl_Review")).download_as_string()
    soup = BeautifulSoup(one_str, 'html.parser')
    # f'https://storage.cloud.google.com/{GS_OUTPUTS.name}/{filename.replace("prod1", "yCrawl_Review")}'

    cook_accor(soup)

# %%

#%%
def read_local(EX_RATES):
    ecb = get_ecb_rate(EX_RATES)
    df_hotels_final = finalize_df_hotels(read_parquet("hotels.gzip"), ecb, upload=False)
    df_flights_final = finalize_df_flights(read_parquet("flights.gzip"), ecb, upload=False)

#%%
# df_errs = read_parquet("20220301_errs.parquet.gzip")
def local_test():
    df_flights = read_parquet("20220301_flights.parquet.gzip")
    df_hotels = read_parquet("20220301_hotels.parquet.gzip")

    ecb = get_ecb_rate()
    dff = finalize_df_flights(df_flights, ecb, upload=False)
    dfh = finalize_df_hotels(df_hotels, ecb, upload=False)
    send_summary(dff, dfh, True)


# %%
def iter_local():
    from os import listdir
    fs = [x for x in listdir() if "_flights.par" in x]
    hs = [x for x in listdir() if "_hotels.par" in x]

    ecb = get_ecb_rate()

    for xxx in sorted(fs):
        df = read_parquet(xxx)
        print(f"processing {xxx}")
        finalize_df_flights(df, ecb)

    for xxx in sorted(hs):
        df = read_parquet(xxx)
        print(f"processing {xxx}")
        finalize_df_hotels(df, ecb)


def multi_example(ALL_FILES, N_CORES, GS_ARCHIVE, assemble_dataframe, TAG_Ym, TAG_Ymd):
    # multi-core processing is deprecated due to BS4's deep recursion
    from multiprocessing import Pool

    n_process, i = int(len(ALL_FILES) / N_CORES / 2), 0
    list_of_file_lists = []
    while (i * n_process) < len(ALL_FILES):
        start, end = (i*n_process), min((i+1)*n_process, len(ALL_FILES))
        list_of_file_lists.append(ALL_FILES[start:end])
        i+=1
 
    with Pool(processes=N_CORES) as pool:
        res = pool.map(assemble_dataframe, list_of_file_lists)

    # pooling multi-core results
    all_df_hotels, all_df_flights, all_df_errs, all_hotels_failed, all_files_exception = [], [], [], [], []
    for i, (df_hotels, df_flights, df_errs, hotels_failed, files_exception, bigstr) in enumerate(res):
        all_df_hotels += df_hotels
        all_df_flights += df_flights
        all_df_errs += df_errs
        all_hotels_failed += hotels_failed
        all_files_exception += files_exception

        blob = GS_ARCHIVE.blob(f'BIGSTR/{TAG_Ym}{TAG_Ymd}_BIG{i:02}X.txt')
        blob.upload_from_string(bigstr)



# %% Get old ACR from local files
def get_old_acr_from_local(EX_RATES):
    from bs4 import BeautifulSoup
    from glob import glob
    from tqdm import tqdm
    from pandas import DataFrame, concat
    from sys import argv

    dir = "/Users/pannnyan/Downloads/ACR/**/*.pp"
    filelist = glob(dir, recursive=True)
    filelist = sorted(filelist)

    list_hotels, list_failed = [], []
    for x in tqdm(filelist):
        with open(str(x)) as f:
            one_str = f.read()

        if one_str[:20].split(",")[0] != "output ok":
            continue

        try:
            soup = BeautifulSoup(one_str, 'html.parser')
            cico = [datetime.strptime(x.strip(), "%B %d, %Y").date()
                    for x in soup.select_one("p.basket-hotel-info__stay").get_text().split("\n") if x.strip() !=""]
            nights = int((cico[1] - cico[0]).days)
            json_list = [{
                "hotel": soup.select_one("h3.basket-hotel-info__title").get_text(strip=True),
                "room_type": room.select_one("h2").get_text(strip=True),
                "rate_type": [x.select_one("span").get_text(strip=True) for x in room.select(".offer__options")],
                #"rate_sum_pre": parse_floats(room.select(".offer__price")),
                #"rate_sum_tax": parse_floats(room.select(".pricing-details__taxes")),
                "rate_avg": [(a+b)/nights for a,b in zip(parse_floats(room.select(".offer__price")), 
                                                parse_floats(room.select(".pricing-details__taxes")))],
                "rate_sum": [a+b for a,b in zip(parse_floats(room.select(".offer__price")), 
                                                parse_floats(room.select(".pricing-details__taxes")))],
                "ccy": parse_ccy(room.select(".offer__price")),
                "check_in": cico[0],
                "check_out": cico[1],
                "nights": nights,
                "vmid": "Import-ACR01",
                "ts": soup.timestamp.string
            } for room in soup.select("li.list-complete-item")]

            list_hotels += json_list
        except Exception as e:
            list_failed.append({"filename": x, "exception": str(e)})

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
    df_hotels.to_parquet(f"acr.par", compression='gzip')

    df_hotels_final = finalize_df_hotels(df_hotels, get_ecb_rate(EX_RATES), upload=True)



def copy_n_rename_gs():
    from google.cloud import storage
    from os import system
    bucket = storage.Client().get_bucket("yyyaaannn-us")
    all_files = [x.name for x in bucket.list_blobs(prefix=f'Archives_')]
    cmds = [f"gsutil mv gs://{bucket.name}/{x} gs://{bucket.name}/{x.replace('0000000000', '')}" for x in all_files]
    [system(c) for c in cmds]


def clean_route():
    from json import loads
    from requests import get
    live_meta = get("https://raw.githubusercontent.com/yyyaaan/metadata/main/ycrawl.json")
    iata = loads(live_meta.text)['meta-iata']

    cities = list(iata.keys())
    codes = list(iata.values())
    replace_rec = lambda x, key, value: f"replace({x},\n'{value.upper()}', '{key}')"

    clause = "upper(route)"
    i = 0
    while i < len(iata):
        clause = replace_rec(clause, cities[i], codes[i])
        i += 1

    print(f"update tmpflight set route = \n{clause}")

