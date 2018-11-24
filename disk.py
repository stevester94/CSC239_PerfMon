#! /usr/bin/python
import re
import os
from utils import *

# Main data product is list of these
def get_disk_info():
    keys = ("name", "reads_completed", "reads_merged", "sectors_read", "time_reading_ms", 
            "writes_completed", "writes_merged", "sectors_written", "time_writing_ms",
            "current_IO", "time_doing_IO", "weighted_time_doing_IO")
    f = file("/proc/diskstats")

    disks = []
    for line in f:
        match = re.search(r"\s*[0-9]+\s*[0-9]+\s*(\S*) (.*)", line)

        if "loop" in match.group(1):
            continue

        name = match.group(1)
        stats = [int(s) for s in match.group(2).split(" ")]

        if len([name] + stats) != len(keys):
            print len([name] + stats)
            print len(keys)
            raise ValueException

        d = dict(zip(keys, [name] + stats))
        disks.append(d)
    f.close()


    return disks

def calc_disk_info_rates(prev_list,curr_list,interval):
    assert len(prev_list) == len(curr_list)

    disk_interval_rates = []
    for index,disk in enumerate(curr_list):
        d = {}
        
        for key,_ in disk.iteritems():
            if key == "name":
                d["name"] = curr_list[index]["name"]
                continue
            d[key] = float(curr_list[index][key] - prev_list[index][key]) / interval
        disk_interval_rates.append(d)

    return disk_interval_rates

# Return each disk % used as reported by df
# return array of tuples
# (<device name>, <percent free as float>)
def get_disk_used_space():
    raw_dh_stdout = os.popen("df | grep ^/dev/").read()
    split_lines = raw_dh_stdout.split("\n")
    devices = []
    for line in split_lines:
        if line != None and line != '':
            separated = line.split()
            device = (separated[0], float(separated[4].strip("%"))/100 )
            devices.append(device)
    
    return devices

if __name__ == "__main__":
    print get_disk_used_space()