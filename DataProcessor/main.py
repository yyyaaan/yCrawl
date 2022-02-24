from tqdm import tqdm
from bs4 import BeautifulSoup
from os import environ, listdir
from datetime import datetime
from google.cloud import storage, bigquery
# from pandas_profiling import ProfileReport
import pandas as pd
import re

RUNMODE = "prod1"
FOLDER = "/kaggle/working/gs/"
DATE_TAG = datetime.now().strftime("%Y%m%d")
MSG = ""

