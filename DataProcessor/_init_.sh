#!bin/bash
# calling myself using code below, note for the user name
# git clone https://github.com/yyyaaan/yCrawl
# sudo sh ~/yCrawl/DataProcessor/_init_.sh

apt update && sudo apt -y upgrade
apt install -y python3-pip python-is-python3

# python packages on global level - this a micro service, no virtual env
cd /home/yan/yCrawl
sudo -H pip install -r reqlocal.txt

# authkeys and id
VMID=$HOSTNAME && echo "VMID=$HOSTNAME" | sudo tee -a /etc/environment
AUTHKEY=$(gcloud secrets versions access latest --secret="ycrawl-simple-auth")  && echo "AUTHKEY=$AUTHKEY" | sudo tee -a /etc/environment


# startup script - remove old if exists
rm -f /usr/local/bin/ycrawl-dp.sh /etc/systemd/system/ycrawldp.service
tee -a /usr/local/bin/ycrawl-dp.sh > /dev/null <<EOT
#!/bin/bash

gcloud config set project yyyaaannn
gcloud logging write y_simple_log "test Data Processor Starts" --severity="INFO"

cd /home/yan/yCrawl/
git pull

sudo sh /home/yan/yCrawl/DataProcessor/_startup_.sh

EOT

tee -a /etc/systemd/system/ycrawldp.service > /dev/null <<EOT
# /lib/systemd/system/cloud-final.service
[Unit]
Description=yCrawl Data Processor Auto Start
After=network-online.target cloud-config.service rc-local.service
After=multi-user.target
Before=apt-daily.service
Wants=network-online.target cloud-config.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/ycrawl-dp.sh
RemainAfterExit=yes
TimeoutSec=0
KillMode=process
TasksMax=infinity
StandardOutput=journal+console

[Install]
WantedBy=cloud-init.target

EOT

# verfiy files (printing) 
echo "verfiy start up script and service contents below"
cat /usr/local/bin/ycrawl-dp.sh 
nano /etc/systemd/system/ycrawldp.service
echo "verfiy start up script and service contents above"

chmod 744 /usr/local/bin/ycrawl-dp.sh 
chmod 664 /etc/systemd/system/ycrawldp.service 
systemctl daemon-reload
systemctl enable ycrawldp.service




