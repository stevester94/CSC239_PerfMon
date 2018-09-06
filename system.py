#! /usr/bin/python
import re
from utils import *

def get_cpu_utilization():
    keys = ("cpu_name", "user_mode_ms", "nice_mode_ms", "system_mode_ms", "idle_task_ms", 
            "iowait", "irq", "softirq", "steal", "guest", "guest_nice")

    f = open("/proc/stat", "r")
    cpus = []
 
    for line in f:
        split_line = line.rstrip().split(" ")
        if "cpu" not in split_line[0]:
            continue
        if split_line[0] == 'cpu':
            split_line.remove('')
        for e in range(1, len(split_line)):
            split_line[e] = int(split_line[e])

        if len(split_line) != len(keys):
            print len(split_line)
            print len(keys)
            raise ValueException

        d = dict(zip(keys, split_line))

        cpus.append(d)

    f.close()
    return cpus

def get_interrupts_serviced():
    f = open("/proc/stat", "r")
    
    line = get_first_matching_line(f, "intr")
    split_line = line.rstrip().split(" ")
    print(split_line)

    f.close()
    return int(split_line[1])


def get_context_switches():
    f = open("/proc/stat", "r")

    line = get_first_matching_line(f, "ctxt")
    
    split_line = line.split(" ")

    f.close()
    return int(split_line[1])


def get_meminfo():
    keys = ("free_kbytes", "total_kbytes", "used_percent")
    f = open("/proc/meminfo")

    total = get_first_matching_line(f, "MemTotal")
    free  = get_first_matching_line(f, "MemFree")

    print total
    total = int(re.search(r"[0-9]+", total).group(0))
    free  = int(re.search(r"[0-9]+", free).group(0))
    used_percent = float(total - free)/total

    if len((free,total,used_percent)) != len(keys):
        print len(split_line)
        print len(keys)
        raise ValueException

    d = dict(zip(keys, (free,total,used_percent)))
    
    f.close()
    return d

def get_process_metrics(pid):
    # Still unsure on overall_usage
    # believe the metrics reported by user_mode and kernel mode are returned as ticks
    keys = ("user_mode_ms", "kernel_mode_ms", "overall_usage", "virtual_memory_kb", "physical_memory_kb", "username", "program_name")
    
    
    f = open("/proc/"+pid+"/stat")
    
    
    split_line = f.read().rstrip().split(" ")
    d = {}
    d["user_mode_ms"] = int(split_line[13]) # This needs to be multiplied by ticks
    d["kernel_mode_ms"] = int(split_line[14]) # Again, this is ticks, need to adjust
    d["overall_usage"] = d["user_mode_ms"] + d["kernel_mode_ms"] # This can't be right...
    d["virtual_memory_kb"] = int(split_line[22])/1024
    
    num_pages = int(split_line[23]) # We'll need to get the page size as well
    d["physical_memory_kb"] = num_pages # Stick with this for now
    d["program_name"] = split_line[1][1:-1]
    f.close()

    f = open("/proc/"+pid+"/status")
    line = get_first_matching_line(f, "Uid")
    match = re.search(r"Uid:\s*[0-9]*\s*([0-9]*)", line) # Second group is the "Effective uid"
    d["username"] = match.group(1) # The UID, need to translate this to username
    
    return d
    
    
if __name__ == "__main__":
    print get_process_metrics("self")
    print get_meminfo()
    print get_context_switches()
    print get_interrupts_serviced()
    print get_cpu_utilization()