#!/bin/bash

gcloud logging write y_simple_log "$VMID $1" --severity="INFO"

### configure path and mode carefully
runmode=prod1
cd /home/yan/yCrawl/Worker/cache

### send to cloud storage -m multitasking
gsutil  -q -m \
        -h "Content-Type:text/html" \
        -h "Content-Encoding:gzip" \
        mv -z pp \
        *.pp \
        gs://staging.yyyaaannn.appspot.com/$runmode/$(date +"%Y%m")/$(date +"%d")


### archive to zip, -m remove files, -q quiet, bot png and pp
### zip -q -m $(date +"%Y%m%d_%H%M%S.zip") *.p*

gcloud logging write y_simple_log "$VMID $1 upload succeeded" --severity="INFO"
