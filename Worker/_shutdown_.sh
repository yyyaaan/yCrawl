#! /bin/bash
# will not do logging if called with parameter

if [ $# -eq 0 ]
  then gcloud logging write y_simple_log "Shutdown noticed for $VMID!" --severity="INFO" &> silent.log
fi

### configure path and mode carefully
runmode=test
cd /home/yan/yCrawl/Worker/cache

### send to cloud storage -q quite -m multitasking
gsutil  -q -m \
        -h "Content-Type:text/html" \
        -h "Content-Encoding:gzip" \
        cp -z pp \
        *.pp \
        gs://ycrawl-data/$runmode/$(date +"%Y")/$(date +"%m")/$(date +"%d")


### archive to zip, -m remove files, -q quiet
zip -q -m $(date +"%Y%m%d_%H%M%S.zip") *.pp

if [ $# -eq 0 ]
  then gcloud logging write y_simple_log "Shutdown ready! Uploading arhiving succeeded for $VMID." --severity="INFO"
fi