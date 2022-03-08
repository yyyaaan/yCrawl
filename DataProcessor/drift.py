# %%
from pandas import DataFrame, concat
from datetime import datetime, timedelta
from google.cloud import bigquery
from linehelper import *

BQ_CLIENT = bigquery.Client()

shorten = lambda x: " ".join(str(x).split(" ")[:3] + ["\n >"])


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
        f"{shorten(x[0])} {x[1]:.1f}% (EUR {x[2]:.0f})" 
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
        f"{x[0]} {x[1]:.1f}% (EUR {x[2]:.0f})"  
        for x in monitor[["departure", "eur_drift", "mineur"]].values
        if abs(x[1]) > threshold_price
    ]

    row_drifts = [
        f"(C{days}) {x[0]} {x[1]:.1f}%" 
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

    msg_df = concat([
        DataFrame({"title": "-Hotel price change", "content": price4h}),
        DataFrame({"title": "-Flight price change", "content": price4f}),
        DataFrame({"title": "Hotel vs yesterday", "content": price1h}),
        DataFrame({"title": "Flight vs yesterday", "content": price1f}),
        DataFrame({"title": "_Data quantity drifts", "content": row4h + row4f + row1h + row1f}),
    ])

    send_df_as_flex(
        df=msg_df, msg_endpoint=msg_endpoint, text="Data Drift Summary", 
        color="11", size="xxs", sort=True)

# %%
