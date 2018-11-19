#! /usr/bin/python

from network import *
from system import *
from disk import *
import pprint
from time import sleep
from proc import *
import sys
import json

# This function distills the procs into what will be used by the frontend
# Will probably break this apart, but will serve as an example for now
def distill_procs():
    prev_procs = None
    pp = pprint.PrettyPrinter(indent=4)
    SLEEP_TIME = 1


    desired_keys = [
        "interval_utilization",
        "physical_mem_bytes",
        "username",
        "comm",
        "priority",
        "utime"
    ] # And will have 'pid', embedded in the for loop

    while True:
        procs = dictify_procs(get_all_complete_procs())
        if prev_procs != None:
            populate_all_proc_utilization_interval_percent(prev_procs, procs)
            proc_payload = [] # Will be an array of dicts

            for key,value in procs.iteritems():
                this_proc = {}
                this_proc["pid"] = key
                for desired in desired_keys:
                    this_proc[desired] = value[desired]
                proc_payload.append(this_proc)

            f = open("sample_procs.json", "w")
            f.write(json.dumps(proc_payload))
            f.close()
            print "Great success, exiting"
            exit(0)


                

        prev_procs = procs
        sleep(SLEEP_TIME)

def are_keys_same_as_last(previous_dict, current_dict):
    return set(previous_dict.keys()) == set(current_dict.keys())

def validate_meminfo():
    pp = pprint.PrettyPrinter(indent=4)
    prev_meminfo = None
    SLEEP_TIME = 1

    while True:
        if prev_meminfo != None:
            cur_meminfo = get_meminfo()
            print "Keys are the same?: " +  str(are_keys_same_as_last(prev_meminfo, cur_meminfo))
        prev_meminfo = get_meminfo()
        sleep(SLEEP_TIME)

#Literally just an int
def validate_context_switches():
    pp = pprint.PrettyPrinter(indent=4)
    SLEEP_TIME = 1

    while True:
        pp.pprint(get_context_switches())
        sleep(SLEEP_TIME)

def validate_interrupts_serviced():
    pp = pprint.PrettyPrinter(indent=4)
    SLEEP_TIME = 1

    while True:
        pp.pprint(get_interrupts_serviced())
        sleep(SLEEP_TIME)

# Use as a template for checking other keys
# def validate_disk_info():
#     pp = pprint.PrettyPrinter(indent=4)
#     prev = None
#     SLEEP_TIME = 1

#     while True:
#         cur = get_disk_info()
#         if prev != None:
#             print "Keys are the same?: " +  str(are_keys_same_as_last(prev, cur))
#         prev = cur
#         sleep(SLEEP_TIME)

def validate_disk_info():
    pp = pprint.PrettyPrinter(indent=4)
    prev_keys = None
    SLEEP_TIME = 1

    while True:
        disk_info = get_disk_info()
        for d in disk_info:
            keys = set(d.keys())
            if keys != set(disk_info[0]):
                print "Keys in current set do not match"
                pp.pprint(keys)
                pp.pprint(set(disk_info[0]))
                return
        
            if prev_keys != None:
                if keys != prev_keys:
                    print "Keys in current set do not match previous"
                    pp.pprint(keys)
                    pp.pprint(prev_keys)
                    return
        print "Keys match"
        prev_keys = set(disk_info[0].keys())
        sleep(SLEEP_TIME)

# OK this is getting out of hand
# Going to verify that the keys in each proc does not change
def validate_procs():
    prev_procs = None
    pp = pprint.PrettyPrinter(indent=4)
    SLEEP_TIME = 1

    while True:
        procs = dictify_procs(get_all_complete_procs())
        if prev_procs != None:
            populate_all_proc_utilization_interval_percent(prev_procs, procs)
            last_keys_set = None
            for proc in procs.itervalues():
                if last_keys_set != None:
                    if set(proc.keys()) != last_keys_set:
                        print "Keys are not equivalent :("
                        exit(1)
                    else:
                        print set(proc.keys())
                last_keys_set = set(proc.keys())

        prev_procs = procs
        sleep(SLEEP_TIME)




if __name__ == "__main__":
    if sys.argv[1] == "validate_procs": validate_procs()
    if sys.argv[1] == "distill_procs": distill_procs()
    if sys.argv[1] == "validate_meminfo": validate_meminfo()
    if sys.argv[1] == "validate_context_switches": validate_context_switches()
    if sys.argv[1] == "validate_interrupts_serviced": validate_interrupts_serviced()
    if sys.argv[1] == "validate_disk_info": validate_disk_info()
