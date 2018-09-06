#! /usr/bin/python
import re
from utils import *

def get_disk_reads():
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


if __name__ == "__main__":
    print get_disk_reads()
