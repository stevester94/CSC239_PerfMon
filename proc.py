import re
import sys
from utils import *
from subprocess import Popen, PIPE

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

def get_procs_from_inode(inode, proc_dict):
    procs = []

    for pid,proc in proc_dict.iteritems():
        if inode in proc["socket_inodes"]:
            procs.append(proc)

    return procs


def get_proc_stat(pid):
    keys = ("pid", "comm", "state", "ppid", "pgrp", "session", "tty_nr", "tpgid", "flags", "minflt", "cminflt", "majflt", "cmajflt", "utime", "stime", "cutime", "cstime", "priority", "nice", "num_threads", "itrealvalue", "starttime", "vsize", "rss", "rsslim", "startcode", "endcode", "startstack", "kstkesp", "kstkeip", "signal", "blocked", "sigignore", "sigcatch", "wchan", "nswap", "cnswap", "exit_signal", "processor", "rt_priority", "policy", "delayacct_blkio_ticks", "guest_time", "cguest_time", "start_data", "end_data", "start_brk", "arg_start", "arg_end", "env_start", "env_end", "exit_code")

    path = "/proc/" + pid + "/stat"

    try:
        f = open(path, "r")
    except:
        return None

    line = f.read()
    (first_part, name, status, second_part) = re.match("(\d+) (\(.*?\)) (.) (.*)", line).groups()

    stats = [int(s) for s in second_part.rstrip().split(" ")]

    final = [first_part,] + [name,] + [status,] + stats
    
    assert len(keys) == len(final)

    return dict(zip(keys, final))

def get_proc_complete(pid):
    custom_keys = ("username", "utilization", "socket_inodes", "virtual_mem_bytes", "physical_mem_bytes", "running_time") # socket_inodes being an array

    proc_stat = get_proc_stat(pid)
    if proc_stat == None:
        return None
    running_time = get_uptime_clocks()["uptime"] - float(proc_stat["starttime"])
    proc_stat["running_time"] = running_time
    username = get_username(get_uid_from_pid(proc_stat["pid"]))
    utilization = calc_proc_utilization_overall_percent(proc_stat)
    socket_inodes = get_proc_socket_inodes(pid)


    proc_stat["username"] = username
    proc_stat["utilization"] = utilization
    proc_stat["socket_inodes"] = socket_inodes
    proc_stat['virtual_mem_bytes'] = proc_stat["vsize"] # Yes this is correct

    p = Popen(['getconf', 'PAGESIZE'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    page_size, err = p.communicate()
    page_size = int(page_size)
    proc_stat['physical_mem_bytes'] = proc_stat["rss"] * page_size


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

    return float(busy_delta)/total_delta

def dictify_procs(procs):
    d = {}
    for p in procs:
        d[p["pid"]] = p

    return d

# Fill in interval_utilization for current_procs
def populate_all_proc_utilization_interval_percent(prev_procs, current_procs):

    for pid,proc in current_procs.iteritems():
        if pid not in prev_procs:
            print "Setting interval_utilization to 0 for %s" % pid
            current_procs[pid]["interval_utilization"] = 0
            continue # Skip processes that are so new they aren't in the last sweep
        previous = prev_procs[pid]
        current  = proc
        current_procs[pid]["interval_utilization"] = calc_proc_utilization_interval_percent(previous, current)

# Return a list of (pid, interval_utilization) sorted descending by interval_utilization
def sort_procs_by_interval_utilization(procs):
    proc_list = [(pid, proc["interval_utilization"]) for pid,proc in procs.iteritems()]
    proc_list.sort(key=lambda x: x[1], reverse=True)

    return proc_list

def get_proc_highlights(proc_dict):
    highlights_keys = ("username", "comm", "virtual_mem_bytes", "physical_mem_bytes", "interval_utilization")
    highlights = []
    for h in highlights_keys:
        if h in proc_dict:
            highlights.append(str(proc_dict[h]))

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
        proc = get_proc_complete(pid)
        if proc != None:
            procs.append(proc)
        else:
            if pid in get_all_pids():
                print "this is a weird situation, the defunct pid really does exist!"
                sys.exit(1)


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