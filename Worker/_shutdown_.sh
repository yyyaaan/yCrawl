#! /bin/bash
# managed in compute instance, config path carefully
# further reference: https://cloud.google.com/compute/docs/instances/create-use-preemptible#handle_preemption

gcloud logging write y_simple_log 'Shutdown noticed for $HOSTNAME!'

### configure path and mode carefully
runmode=test
cd /home/yan/yCrawl/Worker/cache

### send to cloud storage ###
gsutil  -m \
        -h "Content-Type:text/html" \
        -h "Content-Encoding:gzip" \
        cp -z pp \
        *.pp \
        gs://ycrawl-data/$runmode/$(date +"%Y")/$(date +"%m")/$(date +"%d")


### archive to zip, -m remove files, -q quiet
zip -q -m $(date +"%Y%m%d_%H%M%S.zip") *.pp

gcloud logging write y_simple_log 'Shutdown ready! Uploading arhiving succeeded for $HOSTNAME.'

### really power off
systemctl poweroff
