#!/bin/bash
# run this file in working directory
# dependencies installer (apt-get, pupeteer/nodejs )
# this is a bash script for Ubuntu, changes needed for other environment

apt-get install -y \
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
    xdg-utils

# node.js 
curl -fsSL https://deb.nodesource.com/setup_17.x | sudo -E bash -
apt-get install -y nodejs

# single line gsutil
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - && apt-get update -y && apt-get install google-cloud-sdk -y

# package.json
npm install

# export GOOGLE_APPLICATION_CREDENTIALS="path/to/json"
gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS

# python seems no extra package needed
# pip install -r requirements.txt

# cache directory
mkdir cache
