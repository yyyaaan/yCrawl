#! /bin/bash
# only required on local development envrionment

source activate base

export GOOGLE_APPLICATION_CREDENTIALS="~/Documents/.credentials/gcp.json"
export AUTHKEY=$(gcloud secrets versions access latest --secret="ycrawl-simple-auth")
export VMID="local-mac-os"