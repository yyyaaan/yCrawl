from google.cloud import storage, bigquery
from json import loads

CHECK_DATE = "202203/16"
GS_OUTPUTS = storage.Client(project="yyyaaannn").get_bucket("yyyaaannn-us")
BQ_CLIENT = bigquery.Client()

# metaname = f"yCrawl_Output/{CHECK_DATE.split('/')[0]}/{CHECK_DATE.replace('/', '')}_meta.json"
# meta = loads(GS_OUTPUTS.get_blob(metaname).download_as_string())

filelist = [x.name for x in GS_OUTPUTS.list_blobs(prefix=f"yCrawl_Review/{CHECK_DATE}")]
filelist_flat = "', '".join([x.replace("yCrawl_Review", "prod1") for x in filelist])

error_msg = (BQ_CLIENT
    .query(f"select errm, filename from yCrawl.issues where filename in ('{filelist_flat}');")
    .result().to_dataframe()
)

