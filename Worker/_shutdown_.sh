#!/bin/bash
# managed in compute instance, config path carefully
# further reference: https://cloud.google.com/compute/docs/instances/create-use-preemptible#handle_preemption

echo Shutdown noticed! $(date +"%c")


### configure path and mode carefully
runmode=test
cd ./cache

### send to cloud storage ###
gsutil  -m \
        -h "Content-Type:text/html" \
        -h "Content-Encoding:gzip" \
        cp -z pp \
        *.pp \
        gs://ycrawl-data/$runmode/$(date +"%Y")/$(date +"%m")/$(date +"%d")


### archive to zip, -m remove files, -q quiet
zip -q -m $(date +"%Y%m%d_%H%M%S.zip") *.pp

echo Shutdown ready! Uploading arhiving succeeded on $(date +"%c")
