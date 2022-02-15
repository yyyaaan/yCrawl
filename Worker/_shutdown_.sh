#! /bin/bash
# will not do logging if called with parameter

if [ $# -eq 0 ]
  then gcloud logging write y_simple_log "$VMID shutdown request acknowledged" --severity="INFO" &> silent.log
  else gcloud logging write y_simple_log "$VMID $1" --severity="INFO" &> silent.log
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


### archive to zip, -m remove files, -q quiet, bot png and pp
zip -q -m $(date +"%Y%m%d_%H%M%S.zip") *.p*

if [ $# -eq 0 ]
  then gcloud logging write y_simple_log "$VMID shutdown ready, upload succeeded" --severity="INFO"
  else gcloud logging write y_simple_log "$VMID $1 upload succeeded" --severity="INFO" &> silent.log
fi