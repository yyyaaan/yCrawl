#!/bin/bash

gcloud logging write y_simple_log "Data Processor VM initiated" --severity="INFO"
AUTHKEY=$(gcloud secrets versions access latest --secret="ycrawl-simple-auth")

# call the main.py 
cd /home/yan/yCrawl/DataProcessor/
nohup python3 -u main.py > /home/yan/dataprocessor.log 2>&1 &

