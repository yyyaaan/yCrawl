# yCrawl
My Web Crawl is a collection of daily-repetitive web scrapping tasks. Main language is `python` (main) and `node.js` (for puppeteer only), and are usually commanded by `bash` scripts for system control.

## Roles

The folder structure is organized according to roles. The root folder is for worker. Subfolder Coordiantor and DataProcessor shall be deployed separately.

__Coordinator__ is in charge of distributing tasks and monitoring completion status. Coordinator can be a micro-service, and the code is self-contained in subfolder. Python library is called to use cloud storage for simple deployment.

__Worker__ is a virtual machine (or container) to actually do the job. To simplify process, a worker will only call `main.py` and subsequently calling node and python modules. Cloud interface is achieve directly in `gsutil` bash for better performance.

__DataProcessor__ is the pipeline to perform ETL.

## Other concpets

- In worker, minimal packages are used. For example, GCP operations are hand to gsutil command line. AUTHKEY is managed by Cloud Secret Manager, and registered to system environment dynamically.

## Deployment Checklist
- Configure availablity, meta-data and API access during creation
- Run `__init__.sh` manually (recommended) or git first and call the sh
- Check path and python3, nodejs versions
- Confirm service account rights (bucket, secret accessor)
- Scripts settings in metadata `#! /bin/bash sudo sh /home/yan/yCrawl/Worker/_shutdown_.sh`

