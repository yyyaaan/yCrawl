# on woker startup

# gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
# gcloud config set project yyyaaannn

# check udpated version
cd /home/yan/yCrawl
git pull

# call the main.py and done
cd /home/yan/yCrawl/Worker
python3 main.py &

# logging
gcloud logging write y_simple_log "VM $HOSTNAME Startup"

