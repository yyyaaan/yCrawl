from os import system, getenv
from time import sleep
from json import loads
from random import random
from datetime import datetime
from requests import post as urlpost, get as urlget


profile = urlget("https://raw.githubusercontent.com/yyyaaan/metadata/main/ycrawl.json")
meta = loads(profile.text)['worker-profile']
N_PER_STAGE = meta["stage-size"]
DELAY_TARGET = meta["delay-target"]
COORDINATOR_ENDPOINT = meta["COORDINATOR_ENDPOINT"]
COMPLETION_ENDPOINT = meta["COMPLETION_ENDPOINT"]

def get_job_list():
    sleep(50*random())
    res = urlpost(COORDINATOR_ENDPOINT, json = {"VMID": getenv("VMID"), "AUTH": getenv("AUTHKEY")})
    jobs = []
    if res.status_code not in [400, 403]:
        jobs = [x for x in res.text.split("\n") if x != ""]
    return jobs


def printT(str):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "  " + str)
    system(f'gcloud logging write y_simple_log "{str}"')
    return True


def run_with_delay(command_list, delay_factor=70):
    nn, nt = 0, len(command_list)
    if nt < 1:
        return True

    printT(f'{getenv("VMID")} starts assigned {nt} jobs')

    for command in command_list:
        system(command + " &")
        nn += 1
        if nn % N_PER_STAGE == 0:
            sleep(90)
            info = f'Stage_{nn}S_{nt-nn}R'
            system(f"sh _shutdown_.sh {info}")
        
        sleep(delay_factor * random())

    return True


def main():
    # preemtible safe operation, can be stopped in the middle
    jobs_todo = get_job_list()
    is_completed = run_with_delay(jobs_todo)

    # preemtible shutdown won't be here; on full completion, retry once
    if is_completed and len(jobs_todo):
        sleep(99)
        system("sh _shutdown_.sh localretry")
        sleep(30)
        run_with_delay(get_job_list())
    
    # after one retry, will shutdown anyway
    sleep(120)
    system("sh _shutdown_.sh lastlocal")
    urlpost(COMPLETION_ENDPOINT, json = {"VMID": getenv("VMID"), "AUTH": getenv("AUTHKEY")})



if __name__ == "__main__":
    main()
