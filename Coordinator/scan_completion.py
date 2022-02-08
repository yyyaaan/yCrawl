from config import *
from os import listdir, getcwd


def get_keys_status(type=RUN_MODE):
    
    # scan saved files, differ from local and server
    if type == 'local':
        cache_folder = getcwd().split("/")
        cache_folder[len(cache_folder)-1] = "cache"
        cache_folder = "/".join(cache_folder)

        files_in_storage = [x for x in listdir(cache_folder) if x.endswith(".pp")]
    else:
        ######### TO BE IMPLEMENTED #########
        files_in_storage = []

    

    keys_completed = [DATE_STR + "_" + x.split("_")[1] for x in files_in_storage if not x.endswith("ERR.pp")]
    # error keys may have duplicates, LIMIT_RETRY to remove it 
    keys_error = [DATE_STR + "_" + x.split("_")[1] for x in files_in_storage if x.endswith("ERR.pp")]
    keys_forfeit = [x for x in keys_error if keys_error.count(x) >= LIMIT_RETRY]
    keys_forfeit = list( dict.fromkeys(keys_forfeit) ) # remove dup
    
    return keys_completed, keys_forfeit, keys_error




