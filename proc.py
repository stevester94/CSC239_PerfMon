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

# In actuality this is more like a map from pid to inodes that it contains
def build_inode_to_pid_map():
    pids =  get_all_pids()

    procs = []

    for pid in pids:
        # print pid
        inodes = get_proc_socket_inodes(pid)
        # print "    " + str(inodes)

        procs.append((pid,inodes))

    return procs


def get_pids_from_inode(inode, the_map):
    pids = []

    for p in the_map:
        if inode in p[2]:
            pids.append(p[0])

    print "pids: " + str(pids)
    return pids


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

def get_proc_complete(pid):
    custom_keys = ("username", "utilization", "socket_inodes", "virtual_mem_bytes", "physical_mem_pages", "running_time") # socket_inodes being an array

    proc_stat = get_proc_stat(pid)
    running_time = get_uptime_clocks()["uptime"] - float(proc_stat["starttime"])
    proc_stat["running_time"] = running_time
    username = get_username(get_uid_from_pid(proc_stat["pid"]))
    utilization = calc_proc_utilization_overall_percent(proc_stat)
    socket_inodes = get_proc_socket_inodes(pid)


    proc_stat["username"] = username
    proc_stat["utilization"] = utilization
    proc_stat["socket_inodes"] = socket_inodes
    proc_stat['virtual_mem_bytes'] = proc_stat["vsize"]
    proc_stat['physical_mem_pages'] = proc_stat["rss"]


    return proc_stat




def calc_proc_utilization_overall_percent(proc_dict):
    user_time = proc_dict["utime"]
    system_time = proc_dict["stime"]
    total_time = proc_dict["running_time"]

    return float(user_time + system_time) / total_time

def calc_proc_utilization_interval_percent(prev, current):
    def _calc_time_busy(d):
        return d["utime"] + d["stime"]

    def _calc_total_time(d):
        return d["running_time"]

    busy_delta = _calc_time_busy(current) - _calc_time_busy(prev)
    total_delta = _calc_total_time(current) - _calc_time_busy(prev)

    return busy_delta/total_delta

# Fill in interval_utilization for current_procs
def populate_all_proc_utilization_interval_percent(prev_procs, current_procs):
    for p,c in zip(prev_procs, current_procs):
        c["interval_utilization"] = calc_proc_utilization_interval_percent(p,c)

    for c in current_procs:
        assert "interval_utilization" in c

def get_proc_highlights(proc_dict):
    highlights_keys = ("username", "comm", "virtual_mem_bytes", "physical_mem_pages", "interval_utilization")

    highlights = {}
    for h in highlights:
        if h in proc_dict:
            highlights[h] = proc_dict[h]

    return highlights

# return lis of pids
def get_all_pids():
    thedir = "/proc/"
    dirs = [name for name in os.listdir(thedir) if os.path.isdir(os.path.join(thedir, name)) ]

    procs = []
    for pid in dirs:
        if re.match("([0-9]+)", pid):
            procs.append(pid)

    return procs

def get_all_complete_procs():
    procs = []
    for pid in get_all_pids():
        procs.append(get_proc_complete(pid))

    return procs

def get_uid_from_pid(pid):
    path = "/proc/" + pid + "/status"
    f = open(path)

    line = get_first_matching_line(f, "Uid")
    return re.search("\d+", line).group(0)

if __name__ == "__main__":
    print get_all_pids()
    for pid in get_all_pids():
        proc_stat = get_proc_complete(pid)
        print proc_stat
        break
        print proc_stat["comm"]
        print "    utilization: " + str(proc_stat["utilization"])
        print "    socket inodes: " + str(proc_stat["socket_inodes"])
        print "    username: " + str(proc_stat["username"])
        print "===================================================================="