#! /bin/bash
echo entering startup script
gcloud logging write y_simple_log "VM $VMID Starting"

# update to version
cd home/yan/yCrawl/
git pull

# call the main.py and done
cd ./Worker/
nohup python3 main.py &

gcloud logging write y_simple_log "VM $VMID Job initiated"
echo completed startup script