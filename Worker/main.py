from os import system, getenv
from time import sleep
from random import random
from datetime import datetime
from requests import get as urlget, post as urlpost

RUN_MODE = "test"
COORDINATOR_ENDPOINT = "http://app.yan.fi/coordinator"
COMPLETION_ENDPOINT = "http://app.yan.fi/notifydone"
#COMPLETION_ENDPOINT = "http://127.0.0.1:8080/notifydone"
#urlpost(COMPLETION_ENDPOINT, data = {"VMID": getenv("VMID")})

def get_job_list():
    res = urlget(COORDINATOR_ENDPOINT)
    jobs = [x for x in res.text.split("\n") if x != ""]
    return jobs


def printT(str):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "  " + str)
    system(f'gcloud logging write y_simple_log "{str}"')
    return True


def run_with_delay(command_list, delay_factor=30):
    nn, nt = 0, len(command_list)
    printT(f"#Jobs = {nt}")

    for command in command_list:
        system(command + " &")
        nn += 1
        if nn % 10 == 0:
            printT(f"Submitted {nn} Remaining {nt-nn}")
        
        sleep(delay_factor * random())

    return True


def main():
    jobs = get_job_list()
    
    # preemtible safe operation, can be stopped in the middle
    is_completed = run_with_delay(jobs)

    # preemtible exit won't reach here, only full completion reach, shutdown will trigger registered shutdown script
    if is_completed:
        sleep(90)
        urlpost(COMPLETION_ENDPOINT, json = {"VMID": getenv("VMID")})



if __name__ == "__main__":
    main()
