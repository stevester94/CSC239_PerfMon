#! /usr/bin/python
import re
from utils import *

def get_disk_reads():
    keys = ("reads_completed", "reads_merged", "sectors_read", "time_reading_ms", 
            "writes_completed", "writes_merged", "sectors_written", "time_writing_ms",
            "current_IO", "time_doing_IO", "weighted_time_doing_IO")
    f = file("/proc/diskstats")

    lines = search_all_lines_with_regex(f, "sd[a-z][0-9]*")
    disks = []
    for line in lines:
        match = re.search("(sd[a-z][0-9]*) (.*)", line)
        name = match.group(1)
        stats = [int(s) for s in match.group(2).split(" ")]
        d = dict(zip(keys, [name] + stats))
        disks.append(d)
    f.close()
    return disks


if __name__ == "__main__":
    print get_disk_reads()
