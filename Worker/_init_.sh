#!/bin/bash
# Unbuntu 20.04 tested. dependencies installer (apt-get, pupeteer/nodejs )

# fully automated requires 1) .gcp.json 2) user created, both can be done in 3rd part tools
# scp -i csc.pem gcp-ycrawl.json ubuntu@ip:/.gcp.json
# scp -i csc.pem /src/_init_.sh ubuntu@ip:~/init.sh 

VMID=ycrawl-8-csc
apt-get upgrade -y

# add new NodeJS to repo, will run apt-update automatically

curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -


apt-get install -y \
    apt-transport-https \
    ca-certificates \
    fonts-liberation \
    gconf-service \
    git \
    gnupg \
    libappindicator1 \
    libasound2 \
    libatk1.0-0 \
    libcairo2 \
    libcups2 \
    libfontconfig1 \
    libgbm-dev \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libicu-dev \
    libjpeg-dev \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpng-dev \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    nodejs \
    xdg-utils \
    zip

# one-line gcloud
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - && sudo apt-get update -y && sudo apt-get install google-cloud-sdk -y


cd /home/yan

git clone https://github.com/yyyaaan/yCrawl

cd /home/yan/yCrawl/Worker
npm install
mkdir cache



#   _____    _            _   _ _         
#  |_   _|  | |          | | (_) |        
#    | |  __| | ___ _ __ | |_ _| |_ _   _ 
#    | | / _` |/ _ \ '_ \| __| | __| | | |
#   _| || (_| |  __/ | | | |_| | |_| |_| |
#  |_____\__,_|\___|_| |_|\__|_|\__|\__, |
#                                    __/ |
#                                   |___/ 

# GCP service account, if necessary
GOOGLE_APPLICATION_CREDENTIALS="/.gcp.json" && echo "GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS" | sudo tee -a /etc/environment
gcloud config set project yyyaaannn
gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS

# Configuration to tell coordinator
echo "VMID=$VMID" | sudo tee -a /etc/environment
AUTHKEY=$(gcloud secrets versions access latest --secret="ycrawl-simple-auth")  && echo "AUTHKEY=$AUTHKEY" | sudo tee -a /etc/environment
tttoken=$(gcloud secrets versions access latest --secret="ycrawl-token")  && echo "tttoken=$tttoken" | sudo tee -a /etc/environment



#                 _                        _   _                             _       _       
#      /\        | |                      | | (_)                           (_)     | |      
#     /  \  _   _| |_ ___  _ __ ___   __ _| |_ _  ___  _ __    ___  ___ _ __ _ _ __ | |_ ___ 
#    / /\ \| | | | __/ _ \| '_ ` _ \ / _` | __| |/ _ \| '_ \  / __|/ __| '__| | '_ \| __/ __|
#   / ____ \ |_| | || (_) | | | | | | (_| | |_| | (_) | | | | \__ \ (__| |  | | |_) | |_\__ \
#  /_/    \_\__,_|\__\___/|_| |_| |_|\__,_|\__|_|\___/|_| |_| |___/\___|_|  |_| .__/ \__|___/
#                                                                             | |            
#                                                                             |_|            

sudo rm /usr/local/bin/ycrawl-startup.sh /etc/systemd/system/ycrawl-init.service
sudo rm /usr/local/bin/ycrawl-shutdown.sh /etc/systemd/system/ycrawl-quit.service

sudo tee -a /usr/local/bin/ycrawl-startup.sh > /dev/null <<EOT
#!/bin/bash

echo "startup script" $(date) >> /home/yan/script.txt
gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
gcloud config set project yyyaaannn
gcloud logging write y_simple_log "test $VMID startup service" --severity="INFO"

cd /home/yan/yCrawl/
git pull

sudo sh /home/yan/yCrawl/Worker/_startup_.sh

EOT

sudo tee -a /etc/systemd/system/ycrawl-init.service > /dev/null <<EOT
# /lib/systemd/system/cloud-final.service
[Unit]
Description=yCrawl init on system startup
After=network-online.target cloud-config.service rc-local.service
After=multi-user.target
Before=apt-daily.service
Wants=network-online.target cloud-config.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/ycrawl-startup.sh
RemainAfterExit=yes
TimeoutSec=0
KillMode=process
TasksMax=infinity
StandardOutput=journal+console

[Install]
WantedBy=cloud-init.target

EOT


# Shutdown script and service

sudo tee -a /usr/local/bin/ycrawl-shutdown.sh > /dev/null <<EOT
#!/bin/bash

echo "shutdown script" $(date) >> /home/yan/script.txt
gcloud logging write y_simple_log "test $VMID shutdown service" --severity="INFO"

sudo sh /home/yan/yCrawl/Worker/_shutdown_.sh ShutdownAcknowledged

EOT


sudo tee -a /etc/systemd/system/ycrawl-quit.service > /dev/null <<EOT
[Unit]
Description=yCrawl safe quit on system shutdown
Wants=network-online.target rsyslog.service
After=network-online.target rsyslog.service
After=snapd.service

[Service]
Type=oneshot
ExecStart=/bin/true
RemainAfterExit=true
ExecStop=/usr/local/bin/ycrawl-shutdown.sh
TimeoutStopSec=0
KillMode=process
StandardOutput=journal+console

[Install]
WantedBy=multi-user.target

EOT


# Activate the services 
# nano /usr/local/bin/ycrawl-shutdown.sh #nano /etc/systemd/system/ycrawl-init.service
sudo chmod 744 /usr/local/bin/ycrawl-startup.sh /usr/local/bin/ycrawl-shutdown.sh
sudo chmod 664 /etc/systemd/system/ycrawl-init.service /etc/systemd/system/ycrawl-quit.service
sudo systemctl daemon-reload
sudo systemctl enable ycrawl-init.service
sudo systemctl enable ycrawl-quit.service

# sudo journalctl -u ycrawl-init.service
