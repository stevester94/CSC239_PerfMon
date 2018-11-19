#! /usr/bin/python

from network import *
from system import *
from disk import *
import pprint
from time import sleep
from proc import *
import sys
import json

pp = pprint.PrettyPrinter(indent=4)


class Distiller:
    def __init__(self):
        self.prev_procs = None
        self.proc_payload = {} # Will be a dict of dicts with pid as primary key

        self.prev_disks = None
        self.disk_payload = {} # Will be a dict of dicts with disk as primary key

        self.system_payload = {}

        self.prev_cpu = None
        self.cpu_payload = {} # Will be a dict of dicts with disk as primary key





    # This function distills the procs into what will be used by the frontend
    # Will probably break this apart, but will serve as an example for now
    def distill_procs(self):

        desired_keys = [
            "interval_utilization",
            "physical_mem_bytes",
            "username",
            "comm",
            "priority",
            "utime"
        ] # With pid as the primary key

        procs = dictify_procs(get_all_complete_procs())
        if self.prev_procs != None:
            populate_all_proc_utilization_interval_percent(self.prev_procs, procs)

            self.proc_payload = {}# Clear if we have anything already

            for pid,value in procs.iteritems():
                this_proc = {}
                for desired in desired_keys:
                    this_proc[desired] = value[desired]
                self.proc_payload[pid] = this_proc

        self.prev_procs = procs
    

    # disk reads, block reads, disk writes, blocks written
    def distill_disks(self):
        disk_info = get_disk_info() # List of disks

        desired_keys = [
            "reads_completed",
            "sectors_read",
            "sectors_written",
            "writes_completed"
        ] # With disk name as primary key

        self.disk_payload = {}


        for disk in disk_info:
            cur_disk_dict = {}

            for k in desired_keys:
                cur_disk_dict[k] = disk[k]
            self.disk_payload[disk["name"]] = cur_disk_dict


    def distill_system(self):
        desired_keys = [
            'free_kbytes',
            'total_kbytes',
            'used_percent',
            "context_switches",
            "interrupts"
        ]

        mem_info = get_meminfo()
        interrupts = get_interrupts_serviced()
        context_switches = get_context_switches()

        # Just hijacking the mem_info dict for lazyness
        mem_info["context_switches"] = context_switches
        mem_info["interrupts"] = interrupts

        self.system_payload = mem_info

    def distill_cpus(self):
        desired_keys = [
            "system_mode_ms",
            "user_mode_ms"
        ] # and interval_utilization, cpu_name as the primary key
        cur_cpu = get_cpu_utilization()

        if self.prev_cpu != None:
            self.cpu_payload = {}

            # Just init the cpu_name primary keys
            for cpu in cur_cpu:
                self.cpu_payload[cpu["cpu_name"]] = {}
            
            for cpu in cur_cpu:
                for key in desired_keys:
                    self.cpu_payload[cpu["cpu_name"]][key] = cpu[key]

            percents = calc_percent_time_busy(self.prev_cpu, cur_cpu)
            for cpu in percents:
                self.cpu_payload[cpu[0]]["interval_utilization"] = cpu[1]

        self.prev_cpu = cur_cpu


###################
# Validation code #
###################

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

def distiller_test():
    distiller = Distiller()

    distiller.distill_disks()

    distiller.distill_procs()
    distiller.distill_procs()

    distiller.distill_system()

    distiller.distill_cpus()
    sleep(5)
    distiller.distill_cpus()

    # Print results
    pp.pprint(distiller.disk_payload)
    pp.pprint(distiller.proc_payload)
    pp.pprint(distiller.system_payload)
    pp.pprint(distiller.cpu_payload)







if __name__ == "__main__":
    if sys.argv[1] == "validate_procs": validate_procs()
    if sys.argv[1] == "validate_meminfo": validate_meminfo()
    if sys.argv[1] == "validate_context_switches": validate_context_switches()
    if sys.argv[1] == "validate_interrupts_serviced": validate_interrupts_serviced()
    if sys.argv[1] == "validate_disk_info": validate_disk_info()
    if sys.argv[1] == "distiller_test": distiller_test()
