# %%
from os import getenv
from bs4 import BeautifulSoup
from pandas import DataFrame, concat, to_datetime
from requests import get, post
from google.cloud import bigquery

###################################
### EUR price are parsed as INTEGER
###################################

# %%
BQ_CLIENT = bigquery.Client()
LINEMSG_ENDPOINT = "http://127.0.0.1:7999/sendline"

# bigquery.enums.WriteDisposition.WRITE_TRUNCATE

def upload_to_bq(df, short_id, write_disposition="WRITE_APPEND"):

    schema = [bigquery.SchemaField(str(x), "INT64") for x in df.columns if str(x).startswith("eur")]

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=write_disposition,
    )

    return BQ_CLIENT.load_table_from_dataframe(
        dataframe=df, 
        destination=f"yyyaaannn.yCrawl.{short_id}", 
        job_config=job_config
    ).result()


# %% ERRORS: coalasce node- and cook-time errors
def finalize_df_errs(df_errs, files_exception, upload=True):
    df_ex = DataFrame(files_exception)
    df_ex['type'] = "Exception"
    df_errs['type'] = "Runtime"

    if upload:
        upload_to_bq(concat([df_errs, df_ex]), "issues")
    return True


# %% Exchange rate
def get_ecb_rate():
    try:
        ecb = get("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml")
        soup = BeautifulSoup(ecb.text, "html.parser")
        ecb_list = [x.attrs for x in soup.select("Cube")]
        ecb_list = [{"currency": str(x["currency"]), "rate": float(x["rate"])} for x in ecb_list if 'rate' in x.keys()]
        ecb_list.append({"currency": "EUR", "rate": 1.0 })
        ecb_list.append({"currency": "FJD", "rate": 2.38})
        ecb_list.append({"currency": "XPF", "rate": 119.72})
        ecb_list.append({"currency": "AED", "rate": 4.12})
        # no history is hold for ecb rate
        exchange_rate = DataFrame(ecb_list)
        upload_to_bq(exchange_rate, "ECBrate", write_disposition="WRITE_TRUNCATE")
    except:
        exchange_rate = BQ_CLIENT.query("select * from yyyaaannn.yCrawl.ECBrate").result().to_dataframe()
    return exchange_rate


# %% Keep only latest record, currency exchanged
def finalize_df_flights(df_flights, exchange_rate, upload=True):
    df_flights_out = (df_flights
        .groupby(["route", "ddate", "rdate"])
        .agg(ts=("ts", max))
        .merge(df_flights, on=["route", "ddate", "rdate", "ts"], how="left")
        .merge(exchange_rate, left_on=["ccy"], right_on=["currency"], how="left")
    )
    df_flights_out["eur"] = round((df_flights_out["price"]/df_flights_out["rate"]).astype(float))
    df_flights_out = df_flights_out[["route", "ddate", "rdate", "eur", "ccy", "price", "ts", "vmid"]]

    if upload:
        upload_to_bq(df_flights_out, "flights")
    return df_flights_out


# %% hotels
def finalize_df_hotels(df_hotels, exchange_rate, upload=True):
    main_keys = ["hotel", "room_type", "rate_type", "check_in", "check_out"]
    df_hotels_out = (df_hotels
        .groupby(main_keys)
        .agg(ts=("ts", max))
        .merge(df_hotels, on=main_keys + ["ts"], how="left")
        .merge(exchange_rate, left_on=["ccy"], right_on=["currency"], how="left")
    )

    df_hotels_out["eur"] = round((df_hotels_out["rate_avg"]/df_hotels_out["rate"]).astype(float))
    df_hotels_out["eur_sum"] = round((df_hotels_out["rate_sum"]/df_hotels_out["rate"]).astype(float))
    df_hotels_out = df_hotels_out[["hotel", "room_type", "rate_type", "nights", "eur", "check_in", "check_out", "eur_sum", "ccy", "rate_avg", "rate_sum", "ts", "vmid"]]

    if upload:
        upload_to_bq(df_hotels_out, "hotels")
    return df_hotels_out




def prepare_flex_msg(dff, dfh, sendline=True):
    dff["ddate"] = to_datetime(dff.ddate)
    dff["weekstart"] = dff.ddate.dt.to_period('W').apply(lambda r: r.start_time)
    dff["title"] = "Flight-QR"
    flights_short = (dff
        .groupby(["title", "weekstart"], as_index=False)
        .agg(best=("eur", min))
    )

    dfh["check_in"] = to_datetime(dfh.check_in)
    dfh["weekstart"] = dfh.check_in.dt.to_period('W').apply(lambda r: r.start_time)
    dfh["title"] = dfh["hotel"]
    hotels_short = (dfh
        [(~dfh.rate_type.str.contains("Non")) & (~dfh.rate_type.str.contains("Prepay"))]
        .groupby(["title", "weekstart"], as_index=False)
        .agg(best=("eur", min))
    )

    # %%
    df_msg = concat([flights_short, hotels_short])
    df_msg['content'] = df_msg.weekstart.dt.strftime("%b-%d") + "  " + df_msg.best.astype(str)

    # use standard python processing
    msg_list = [{"title": x[0], "content": x[1]} for x in df_msg[['title', 'content']].values]

    # %%
    titles = set([x["title"] for x in msg_list])
    bubbles = []
    for t in titles:
        bubbles.append({
            "type": "bubble",
            "size": "micro",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                        "type": "text",
                        "text": str(t),
                        "size": "xs",
                        "color": "#aaaaaa",
                        "wrap": True
                    }] + [{
                        "type": "text",
                        "text": x["content"],
                        "size": "xs",
                        "color": "#aaaaaa",
                        "wrap": True
                    } for x in msg_list if x["title"]==t]
            }
        })

    flex_json = {"type": "carousel", "contents": bubbles}
    if sendline:
        try:
            post(LINEMSG_ENDPOINT, json = {
                "AUTH": getenv("AUTHKEY"), 
                "TO": "cloud",
                "TEXT": "Summary for yCrawl Outputs",
                "FLEX": flex_json
            })
        except Exception as e:
            print(f"failed to post line message due to {str(e)}")

        return True


    return flex_json

