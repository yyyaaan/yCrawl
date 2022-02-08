# need to move all files to external storage. call python or native?
runmode=test

echo Shutdown noticed! $(date +"%c")

### go to cache folder
cd ./cache

### send to cloud storage ###
gsutil  -m \
        -h "Content-Type:text/html" \
        -h "Content-Encoding:gzip" \
        cp -z pp \
        *.pp \
        gs://ycrawl-data/$runmode/$(date +"%Y")/$(date +"%m")/$(date +"%d")


# archive to zip, -m remove files, -q quiet
zip -q -m $(date +"%Y%m%d_%H%M%S.zip") *.pp

echo Shutdown ready! Uploading arhiving succeeded on $(date +"%c")
