#!/bin/bash
# dependencies installer (apt-get, pupeteer/nodejs )
# this is a bash script for Ubuntu, changes needed for other environment

# add new NodeJS to repo, will run apt-update automatically
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -

sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    fonts-liberation \
    gconf-service \
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

git clone https://github.com/yyyaaan/yCrawl

cd ~/yCrawl/Worker

# package.json
npm install

# cache directory
mkdir cache

# register a global variable for logging convenience
echo "VMID=$HOSTNAME" | sudo tee -a /etc/environment
VMID=$HOSTNAME
