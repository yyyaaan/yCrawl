from os import system, getenv
from time import sleep
from random import random
from datetime import datetime
from requests import get as urlget, post as urlpost

RUN_MODE = "test"
N_PER_STAGE = 20
COORDINATOR_ENDPOINT = "https://yyyaaannn.ew.r.appspot.com/coordinator"
COMPLETION_ENDPOINT = "https://yyyaaannn.ew.r.appspot.com/notifydone"


def get_job_list():
    res = urlpost(COORDINATOR_ENDPOINT, json = {"VMID": getenv("VMID")})
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
    is_completed = run_with_delay(get_job_list())

    # preemtible shutdown won't be here; on full completion, retry once
    if is_completed:
        sleep(99)
        system("sh _shutdown_.sh BeginRetry")
        sleep(30)
        run_with_delay(get_job_list())
    
    # after one retry, will shutdown anyway
    sleep(120)
    urlpost(COMPLETION_ENDPOINT, json = {"VMID": getenv("VMID")})



if __name__ == "__main__":
    main()
