from os import system
from time import sleep
from random import random
from datetime import datetime

from scipy import rand


def get_job_list(type="local"):
    if type == "local":
        f = open("published_jobs.txt", "r")
        jobs = f.read().split("\n")
        f.close()
    
    return jobs


def printT(str):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "  " + str)


def run_with_delay(command_list, delay_factor=10):
    nn, nt = 0, len(command_list)
    printT(f"#Jobs = {nt}")

    for command in command_list:
        system(command + " &")
        nn += 1
        if nn % 2 == 0:
            printT(f"Submitted {nn} Remaining {nt-nn}")
        
        sleep(delay_factor * random())

    return True


def main():
    jobs = get_job_list("local")
    
    # preemtible safe operation, can be stopped in the middle
    is_completed = run_with_delay(jobs[100:111:2])

    # preemtible exit wont' reach here, only full completion reach, do samething as early stop
    system("sh _shutdown_.sh")


if __name__ == "__main__":
    main()
