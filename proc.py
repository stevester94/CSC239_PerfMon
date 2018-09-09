import re
import sys
from utils import *

# Gets the inode numbers for the socket file descriptors from the fd dir
def get_proc_socket_inodes(pid):
    path = "/proc/" + pid +"/fd/"

    inodes = []
    for desc in os.listdir(path):
        target = ""
        invalid = False
        try:
            target = os.readlink(path+desc)
            if invalid:
                print "WE REALLY SHOULDN'T GET HERE!"
                sys.exit(1)
        except:
            invalid = True
        if "socket" in target:
            inodes.append(re.search(r"([0-9]+)", target).group(1))
        
    return inodes


def get_proc_stat(pid):
    keys = ("pid", "comm", "state", "ppid", "pgrp", "session", "tty_nr", "tpgid", "flags", "minflt", "cminflt", "majflt", "cmajflt", "utime", "stime", "cutime", "cstime", "priority", "nice", "num_threads", "itrealvalue", "starttime", "vsize", "rss", "rsslim", "startcode", "endcode", "startstack", "kstkesp", "kstkeip", "signal", "blocked", "sigignore", "sigcatch", "wchan", "nswap", "cnswap", "exit_signal", "processor", "rt_priority", "policy", "delayacct_blkio_ticks", "guest_time", "cguest_time", "start_data", "end_data", "start_brk", "arg_start", "arg_end", "env_start", "env_end", "exit_code")
    path = "/proc/" + pid + "/stat"

    f = open(path, "r")

    line = f.read()
    (first_part, name, status, second_part) = re.match("(\d+) (\(.*?\)) (.) (.*)", line).groups()

    stats = [int(s) for s in second_part.rstrip().split(" ")]

    final = [first_part,] + [name,] + [status,] + stats
    
    assert len(keys) == len(final)

    return dict(zip(keys, final))

def calc_proc_utilization(proc_dict):
    user_time = proc_dict["utime"]
    system_time = proc_dict["stime"]
    total_time = get_uptime_clocks()["uptime"] - float(proc_dict["starttime"])

    print user_time
    print system_time
    print total_time

    return float(user_time + system_time) / total_time

# return lis of pids
def get_all_pids():
    thedir = "/proc/"
    dirs = [name for name in os.listdir(thedir) if os.path.isdir(os.path.join(thedir, name)) ]

    procs = []
    for pid in dirs:
        if re.match("([0-9]+)", pid):
            procs.append(pid)

    return procs

if __name__ == "__main__":
    print get_all_pids()
    for pid in get_all_pids():
        proc_stat = get_proc_stat(pid)
        print proc_stat["comm"]
        print "    " + str(calc_proc_utilization(proc_stat))
        print "    " + str(get_proc_socket_inodes(pid))
        print "===================================================================="