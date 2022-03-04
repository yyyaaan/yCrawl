# %%
from google.cloud import bigquery
from datetime import datetime, timedelta
from requests import post
from os import getenv

BQ_CLIENT = bigquery.Client()

shorten = lambda x: " ".join(str(x).split(" ")[:3])


# %% 
def get_hotels_drift_by_day(df_hotels_final, days=1, threshold_price=10, threshold_row=30):

    TAG_DATE = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    hotel_pre = BQ_CLIENT.query(f"""
    select hotel, min(eur) as min_eur, count(*) as n_rows
    from yyyaaannn.yCrawl.hotels
    where substring(ts, 1, 10) = "{TAG_DATE}"
    group by hotel
    """).result().to_dataframe()

    monitor = (df_hotels_final
        .groupby("hotel")
        .agg(mineur = ("eur", "min"), nrows = ("eur", "count"))
        .merge(hotel_pre, on=["hotel"], how="outer")
    )
    monitor["eur_drift"] = 100*(monitor["mineur"] - monitor["min_eur"])/monitor["min_eur"]
    monitor["row_drift"] = 100*(monitor["nrows"] - monitor["n_rows"])/monitor["n_rows"]

    price_drifts = [
        f"- {shorten(x[0])} {x[1]:.1f}% (EUR {x[2]:.0f})" 
        for x in monitor[["hotel", "eur_drift", "mineur"]].values
        if abs(x[1]) > threshold_price
    ]

    row_drifts = [
        f"(C{days}) {shorten(x[0])} {x[1]:.1f}%" 
        for x in monitor[["hotel", "row_drift"]].values
        if abs(x[1]) > threshold_row
    ]

    return price_drifts, row_drifts

# %%  
def get_flights_drift_by_day(df_flights_final, days=1, threshold_price=10, threshold_row=30):

    TAG_DATE = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # further simplied to departure city only
    flights_pre = BQ_CLIENT.query(f"""
    select TRIM(REGEXP_EXTRACT(route, r'\w+\s+')) as departure, min(eur) as min_eur, count(*) as n_rows
    from yyyaaannn.yCrawl.flights
    where substring(ts, 1, 10) = "{TAG_DATE}"
    group by TRIM(REGEXP_EXTRACT(route, r'\w+\s+'))
    """).result().to_dataframe()

    df_flights_final["departure"] = df_flights_final['route'].str.split(' ').str[0]

    monitor = (df_flights_final
        .groupby("departure")
        .agg(mineur = ("eur", "min"), nrows = ("eur", "count"))
        .merge(flights_pre, on=["departure"], how="outer")
    )
    monitor["eur_drift"] = 100*(monitor["mineur"] - monitor["min_eur"])/monitor["min_eur"]
    monitor["row_drift"] = 100*(monitor["nrows"] - monitor["n_rows"])/monitor["n_rows"]

    price_drifts = [
        f"- Flight from {x[0]} {x[1]:.1f}% (EUR {x[2]:.0f})"  
        for x in monitor[["departure", "eur_drift", "mineur"]].values
        if abs(x[1]) > threshold_price
    ]

    row_drifts = [
        f"(C{days}) {shorten(x[0])} {x[1]:.1f}%" 
        for x in monitor[["departure", "row_drift"]].values
        if abs(x[1]) > threshold_row
    ]

    return price_drifts, row_drifts


# %%  
def send_drift(df_flights_final, df_hotels_final, msg_endpoint):

    price1h, row1h = get_hotels_drift_by_day(df_hotels_final, 1)
    price4h, row4h = get_hotels_drift_by_day(df_hotels_final, 4)
    price1f, row1f = get_flights_drift_by_day(df_flights_final, 1)
    price4f, row4f = get_flights_drift_by_day(df_flights_final, 4)

    price1, price4 = price1h + price1f, price4h + price4f
    row1, row4 = row1h + row1f, row4h + row4f
    price1 = ["Price drift from yesterday's data:"] + price1 if len(price1) else price1
    price4 = ["Significant price change over same period:"] + price4 if len(price4) else price4
    row14 = ["Data quantity drift"] + row4 + row1
    outlist = price4 + price1 if len(row14)==1 else price4 + price1 + row14
    msg_txt = "\n".join(outlist) if len(outlist) else "No significant price change or data drift detected"

    if len(msg_endpoint)>10:
        try:
            res = post(msg_endpoint, json = {
                "AUTH": getenv("AUTHKEY"), 
                "TO": "cloud",
                "TEXT": msg_txt,
            })
            print(f"{res.status_code} {res.text}")                
        except Exception as e:
            print(f"failed to post line message due to {str(e)}")
