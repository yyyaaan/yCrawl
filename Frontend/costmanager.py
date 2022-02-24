from config import *
from Frontend.functions import get_secret
from boto3 import client as awsclient
from datetime import datetime, timedelta

SECRET = loads(get_secret("ycrawl-credentials"))

def aws_cost(days=14):
    aws_res =  awsclient(
        "ce",
        region_name = 'eu-north-1',
        aws_access_key_id=SECRET['AWS_ACCESS_KEY'],
        aws_secret_access_key=SECRET['AWS_SECRET']
    ).get_cost_and_usage(
        TimePeriod={
            'Start': (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"), 
            'End': datetime.now().strftime("%Y-%m-%d")
        },
        Granularity='DAILY',
        Metrics=["AmortizedCost"]
    )

    aws_dates = [x['TimePeriod']['Start'] for x in aws_res['ResultsByTime']]
    aws_costs = [float(x['Total']['AmortizedCost']['Amount']) for x in aws_res['ResultsByTime']]
    
    return [{"date": str(x)[5:], "usd": y}for x,y in zip(aws_dates, aws_costs)]
