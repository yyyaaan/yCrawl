#!/bin/bash

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

# send info to my server
curl -d '{"vmid": "'"$VMID"'", "event": "'"$1"'", "info": "upload to staging succeeded"}' \
     -H "Content-Type: application/json"  \
     -H "Authorization: Bearer $tttoken" \
     -X POST https://yan.fi/ycrawl/trails/