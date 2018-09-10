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

        stats = [int(e) for e in split_line[1:]]
        split_line = [split_line[0],] + stats

        if len(split_line) != len(keys):
            print len(split_line)
            print len(keys)
            raise ValueException

        d = dict(zip(keys, split_line))

        # These are originally in cycle (1/100th of a sec), * 10 gives ms
        d["user_mode_ms"] = d["user_mode_ms"]*10
        d["nice_mode_ms"] = d["nice_mode_ms"]*10
        d["system_mode_ms"] = d["system_mode_ms"]*10
        d["idle_task_ms"] = d["idle_task_ms"]*10

        cpus.append(d)

    f.close()
    return cpus

# Return list of (cpu_name, % time busy)
def calc_percent_time_busy(previous, current):
    together = zip(previous, current)

    def _calc_time_busy(d):
        return d["user_mode_ms"] + d["system_mode_ms"]

    def _calc_total_time(d):
        return d["user_mode_ms"] + d["system_mode_ms"] + d["idle_task_ms"]

    times = []
    for p,c in together:
        assert p["cpu_name"] == c["cpu_name"]
        time_busy = _calc_time_busy(c) - _calc_time_busy(p)
        time_total = _calc_total_time(c) - _calc_total_time(p)
        print str(time_busy) + "  " + str(time_total)
        times.append((p["cpu_name"], float(time_busy)/time_total))

    return times

def get_interrupts_serviced():
    f = open("/proc/stat", "r")
    
    line = get_first_matching_line(f, "intr")
    split_line = line.rstrip().split(" ")

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
    
    
if __name__ == "__main__":
    print get_process_metrics("self")
    print get_meminfo()
    print get_context_switches()
    print get_interrupts_serviced()
    print get_cpu_utilization()