#!/bin/bash

gcloud logging write y_simple_log "test $VMID machine started" --severity="INFO"
AUTHKEY=$(gcloud secrets versions access latest --secret="ycrawl-simple-auth")

# git pull (update to new version) - MOVED TO SYSTEM SERVICE

# call the main.py and done
cd /home/yan/yCrawl/Worker/
nohup python3 -u main.py > /home/yan/log_$(date +"%Y%m%d_%H%M").log 2>&1 &

# count possible residual files
NRES=$(ls -1q ./Worker/cache/*.pp | wc -l)
gcloud logging write y_simple_log "$VMID initiated (R$NRES)" --severity="INFO"
