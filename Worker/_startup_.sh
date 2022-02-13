#! /bin/bash
gcloud logging write y_simple_log "VM $VMID Started" --severity="INFO" &> silent.log

# update to version
cd home/yan/yCrawl/
git pull

# call the main.py and done
cd ./Worker/
nohup python3 -u main.py > ./cache/0_log_$(date +"%H%M").pp 2>&1 &

# count possible residual files
NRES=$(ls -1q ./Worker/cache/*.pp | wc -l)
gcloud logging write y_simple_log "i $VMID Job initiated ($NRES)" --severity="INFO" &> silent.log