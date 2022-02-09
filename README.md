# yCrawl
My Web Crawl is a collection of daily-repetitive web scrapping tasks. Main language is `python` (main) and `node.js` (for puppeteer only), and are usually commanded by `bash` scripts for system control.

## Roles

The folder structure is organized according to roles. The root folder is for worker. Subfolder Coordiantor and DataProcessor shall be deployed separately.

__Coordinator__ is in charge of distributing tasks and monitoring completion status. Coordinator can be a micro-service, and the code is self-contained in subfolder. Python library is called to use cloud storage for simple deployment.

__Worker__ is a virtual machine (or container) to actually do the job. To simplify process, a worker will only call `main.py` and subsequently calling node and python modules. Cloud interface is achieve directly in `gsutil` bash for better performance.

__DataProcessor__ is the pipeline to perform ETL.

## Environment

Configured environments for `export GOOGLE_APPLICATION_CREDENTIALS="/Users/pannnyan/Documents/.credentials/gcp.json"`

Note: shutdown and startup script is installed in compute instance, and manage externally

## Other concpets
- appdata.json defines tasks should be done; this file is expected to be changed a few times a year
- worker Only use simple infrastructure with Node+Puppeteer and Python. This is to be configured in a preemptible instance.§
