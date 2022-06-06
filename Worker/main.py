from os import system, getenv
from time import sleep
from json import loads
from html import unescape
from random import random
from datetime import datetime
from requests import post as urlpost, get as urlget


meta = urlget ("https://yan.fi/ycrawl/configs/worker/")
meta = loads(meta.text)
N_PER_STAGE = meta["stage-size"]
DELAY_TARGET = meta["delay-target"]
COORDINATOR_ENDPOINT = meta["COORDINATOR_ENDPOINT"]
COMPLETION_ENDPOINT = meta["COMPLETION_ENDPOINT"]
LOGGING_ENDPOINT = "https://yan.fi/ycrawl/trails/"

def get_job_list():

    attemps = 0
    while attemps < 10:
        sleep(50*random())
        res = urlget(COORDINATOR_ENDPOINT, headers={"Authorization": f"Bearer {getenv('tttoken')}"}, params = {"vmid": getenv("VMID")})
        print(res.status_code)
        if res.status_code < 300:
            break
        else:
            attemps += 1
    try:
        jobs = [x for x in res.text.split("\n") if x != ""]
    except:
        jobs = []
    return jobs


def printT(the_str):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "  " + the_str)
    # not very import, if fail just give up
    try:
        urlpost(
            LOGGING_ENDPOINT, 
            headers={"Authorization": f"Bearer {getenv('tttoken')}"}, 
            json = {"vmid": getenv("VMID"), "event": "in progress", "info": the_str}
        )
        return True
    except:
        return False



def run_with_delay(command_list, delay_factor=DELAY_TARGET):
    nn, nt = 0, len(command_list)
    if nt < 1:
        return True

    printT(f'{getenv("VMID")} starts assigned {nt} jobs')

    for command in command_list:
        system(unescape(command) + " &")
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
        system("sh _shutdown_.sh LocalRetry1")
        sleep(30)
        run_with_delay(get_job_list())
        sleep(99)
        system("sh _shutdown_.sh LocalRetry2")
        sleep(30)
        run_with_delay(get_job_list())
    
    # after retry, will shutdown anyway
    sleep(120)
    system("sh _shutdown_.sh LocalRetryFinal")

    # notify done
    while True:
        sleep(50*random())
        res = urlpost(COMPLETION_ENDPOINT, headers={"Authorization": f"Bearer {getenv('tttoken')}"}, json = {"vmid": getenv("VMID")})
        if res.status_code < 300:
            break
        else:
            attemps += 1

if __name__ == "__main__":
    main()