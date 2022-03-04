# yCrawl
My Web Crawl is a collection of daily-repetitive web scrapping tasks. Main language is `python` (main) and `node.js` (for puppeteer only), and are usually commanded by `bash` scripts for system control.

For monitoring, use dedicated server is better than GAE.

## Roles

The folder structure is organized according to roles. Root folder is intended for frontend use with Coordinator and is coded with compatibility of App Engine. Subfolder Worker and DataProcessor shall be deployed separately as simple scipt.

__Frontend__ acts as Flask app, which further includes templates folder. No static folder/content is severed here.

__Coordinator__ is in charge of distributing tasks and monitoring completion status. Coordinator can be a standalone micro-service, but is currently served by Frontend mostly.

__Worker__ is a virtual machine (or container) to actually do the job. To simplify process, a worker will only call `main.py` and subsequently calling node and python modules. Cloud interface is achieve directly in `gsutil` bash for better performance.

__DataProcessor__ is the pipeline to perform ETL. Dedicated Spot instance with montioring agent installed.

__Messenger__ is webhook service, only for VM/local version, not in GAE

## Frontend Coordinator

Stop signal includes Spot Instance interruption (Preemptible Notice), VM manager stop and manual stop. Spot instance should have sufficient time to complete the upload job when interrupted by platform; the stop service is registered in each Worker and is fail-safe.

```mermaid
flowchart LR
    subgraph App-Engine
    S(Cron Init) --> VM{VM Management}
    CO[/Coordinator/]
    CE[/Completion Notice/] -.->|Request Stop| VM
    AllDone{Crawl Completion}
    end

    subgraph Multi-Cloud-VMs
    direction LR
    AWS & Azure & GCP
    end

    subgraph Storage
    BucketS[(Staging Bucket)]
    BucketO[(Output Bucket)]
    BQ[(BigQuery/SQL DB)]
    end

    subgraph Dedicated-Processors
    DP(Data Processor)
    UP(Data Upload Service)
    M(Monitoring Interface)
    MSG(Real-time Messeging & Reporting)
    end

    VM -->|Start| Multi-Cloud-VMs -.->|All Done| CE -.-> AllDone
    VM -.->|Stop| Multi-Cloud-VMs
    CO -.->|Job Assignment| Multi-Cloud-VMs -.->|Notify Availability| CO
    Multi-Cloud-VMs -->|On Stopping| BucketS

    AllDone -->|All Completed| DP
    BucketS --> DP -->|Raw-Parquet| BucketO -->|File Trigger?| UP --> BQ

    BQ --> Dashboard
```
### VM Manager and Status

There are huge differences among cloud services for VM status. "Terminated" for GCP, "Stopped/Deallocated" for Azure, "Stopped" for AWs. Special attention for Azure, stopped VM are still chargeable as deallocation is required, while others do not.

### Security configuration

No environment key required. Secret keys are managed by cloud secret management service, and is centrally managed.

- Cron job header-auth (only allowed by GAE Cron)
- VM control password controlled
- JSON Auth-key checked before accept notice - will move to bearer

## Deployment and other concepts

In worker, minimal packages are used. For example, GCP operations are hand to gsutil command line. AUTHKEY is managed by Cloud Secret Manager, and registered to system environment dynamically.

### Web Interface Deployment

GAE has only a portion of services available. `main2` is an extension to `main`, where more localized services are included. Local version is to be deployed by `gunicorn`. The file `.gcloudignore` exclude the local versions and relevant code to be deployed in GAE.

Note that GAE does not send any message.

### Worker Deployment
- Configure availability, meta-data and API access during creation
- Run `__init__.sh` manually (recommended) or git first and call the sh
- Check path and python3, nodes versions
- Confirm service account rights (bucket, secret accessor)

### Head Server Deployments and Tests

Temporary deployment at fi-server, will be transited to smaller instances. Workload test is conducted on us-server: small memory is ok, but networking is NOT.

Streaming processing is time-consuming, but provides a good balance between CPU/MEM-laod; that is, local copy method would barely improve speed given limited CPU/MEM.

__NOTE__: ycrawl-head is not auto-updated at this moment

### Beautiful Soup for yCrawl notes

Parse bytes (instead of String) with "html.parser" to avoid excessive speical characters.

Cooked-data is not validated before returing, and will be checked in DataFrame before exploding.

Accor: [ccy, rate_avg] and rate_sum calculated as pre_tax+tax. multiple json, list element.

Four Seasons: [rate_sum] single json, list element.

Hilton: [ccy, rate_sum] single json, list element.

Marriott: [] multiple json, list element.



