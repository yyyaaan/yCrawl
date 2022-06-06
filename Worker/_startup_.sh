#!/bin/bash

# gcloud logging write y_simple_log "test $VMID machine started" --severity="INFO"
AUTHKEY=$(gcloud secrets versions access latest --secret="ycrawl-simple-auth")
tttoken=$(gcloud secrets versions access latest --secret="ycrawl-token")
export tttoken

# call the main.py and done
cd /home/yan/yCrawl/Worker/
nohup python3 -u main.py > /home/yan/log_$(date +"%Y%m%d_%H%M").log 2>&1 &

# count possible residual files
NRES=$(ls -1q ./Worker/cache/ | wc -l)

# send info to my server
curl -d '{"vmid": "'"$VMID"'", "event": "VM-Ready", "info": "initiated R'"$NRES"'"}' \
     -H "Content-Type: application/json"  \
     -H "Authorization: Bearer $tttoken" \
     -X POST https://yan.fi/ycrawl/trails/
