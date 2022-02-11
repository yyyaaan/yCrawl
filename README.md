# yCrawl
My Web Crawl is a collection of daily-repetitive web scrapping tasks. Main language is `python` (main) and `node.js` (for puppeteer only), and are usually commanded by `bash` scripts for system control.

## Roles

The folder structure is organized according to roles. The root folder is for worker. Subfolder Coordiantor and DataProcessor shall be deployed separately.

__Coordinator__ is in charge of distributing tasks and monitoring completion status. Coordinator can be a micro-service, and the code is self-contained in subfolder. Python library is called to use cloud storage for simple deployment.

__Worker__ is a virtual machine (or container) to actually do the job. To simplify process, a worker will only call `main.py` and subsequently calling node and python modules. Cloud interface is achieve directly in `gsutil` bash for better performance.

__DataProcessor__ is the pipeline to perform ETL.

## Environment

Configured environments for `conda env config vars set GOOGLE_APPLICATION_CREDENTIALS="/Users/pannnyan/Documents/.credentials/gcp.json"` (example on local). Fine-tuning default worker service account is assumed on cloud deployment.

Note: [Startup shutdown scripts are critical for preemtible instances](https://cloud.google.com/compute/docs/shutdownscript)


## Other concpets
- appdata.json defines tasks should be done; this file is expected to be changed a few times a year


## Deployment Checklist

- Run `__init__.sh` manually
- Check path and python3, nodejs versions
- Grant bucket access to default service account
- Scripts settings in metadata `#! /bin/bash sudo sh /home/yan/yCrawl/Worker/_shutdown_.sh`

Startup and shutdown script to correct auth (default service account)

