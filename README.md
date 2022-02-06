# yCrawl
My Web Crawl is a collection of daily-repetitive web scrapping tasks. Main language is `python` (main) and `node.js` (for puppeteer only), and are usually commanded by `bash` scripts for system control.

## Roles

__Coordinator__ is in charge of distributing tasks and monitoring completion status. Coordinator can be a micro-service, and the code is self-contained in subfolder.

__Worker__ is a virtual machine (or container) to actually do the job. To simplify process, a worker will only call `main.py` and subsequently calling node and python modules.

## Other concpets
- Pub/sub to mark complete???
- `app.py` defines whether it is a worker (can be preemptible) or a coordinator (persistent VM/service).
-  All `nodejs` job is now using positional parameters that match `appdata['task-config']`
- appdata.json defines tasks should be done; this file is expected to be changed a few times a year
- worker Only use simple infrastructure with Node+Puppeteer and Python. This is to be configured in a preemptible instance.§
Shutdown scripts: send files to cloud storage within 30-second warning Maybe a unix bash is better?
