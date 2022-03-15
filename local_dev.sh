#! /bin/bash
# check uptimes: last reboot | less

source activate base

sudo apt install python3-pip python-is-python3 
git clone https://github.com/yyyaaan/yCrawl
sudo -H pip3 install

#########################################################################
#    ____             _                        _   _       _            
#   / ___|_   _ _ __ (_) ___ ___  _ __ _ __   | \ | | __ _(_)_ __ __  __
#  | |  _| | | | '_ \| |/ __/ _ \| '__| '_ \  |  \| |/ _` | | '_ \\ \/ /
#  | |_| | |_| | | | | | (_| (_) | |  | | | | | |\  | (_| | | | | |>  < 
#   \____|\__,_|_| |_|_|\___\___/|_|  |_| |_| |_| \_|\__, |_|_| |_/_/\_\
#                                                    |___/              
### Set up for yCrawl-Head (DataProcessor) ##############################

# remove if existed
# sudo rm -f /etc/systemd/system/ycrawl-head.service /etc/nginx/sites-enabled/ycrawl-head

sudo tee -a /etc/systemd/system/ycrawl-head.service > /dev/null <<EOT
[Unit]
Description=Gunicorn service to yCrawl Head
After=network.target

[Service]
User=yan
Group=www-data
WorkingDirectory=/home/yan/yCrawl
ExecStart=gunicorn --workers 3 --bind unix:yCrawl.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
EOT

sudo tee -a /etc/nginx/sites-enabled/ycrawl-head > /dev/null <<EOT
server {
    listen 80;
    server_name app.yanpan.fi;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/yan/yCrawl/yCrawl.sock;
    }
}
EOT

sudo chmod 664 /etc/systemd/system/ycrawl-head.service
sudo systemctl daemon-reload
sudo systemctl enable ycrawl-head.service

sudo apt install python3-certbot-nginx
sudo certbot --nginx -d domain


AUTHKEY=$(gcloud secrets versions access latest --secret="ycrawl-simple-auth")  && echo "AUTHKEY=$AUTHKEY" | sudo tee -a /etc/environment

# cron job to update, restart daily - ensure date tag is correct, check `date` to ensure timezone
nano /etc/crontab
15 0    * * *   root    sudo systemctl stop ycrawl-head && cd /home/yan/yCrawl && sudo git pull && sudo systemctl start ycrawl-head
