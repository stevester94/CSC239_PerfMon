#! /usr/bin/python

import os
import re
import pwd

# Just the first line that starts with <starting_match>
def get_first_matching_line(f, starting_match):
    for line in f:
        if starting_match == line[:len(starting_match)]:
            return line.rstrip()
    f.seek(0)
    raise ValueException('No matching line found!')

# All lines that start with <starting_match>
def get_all_lines_start_matching(f, starting_match):
    lines = []
    for line in f:
        if starting_match == line[:len(starting_match)]:
            lines.append(line.rstrip())
    f.seek(0)
    return lines

# Will return just the line, not the matching groups
def search_all_lines_with_regex(f, regex):
    lines = []

    for line in f:
        match = re.search(regex, line)
        if match:
            lines.append(line)
    f.seek(0)
    return lines

# return lis of (pid, path)
def get_all_process_dirs():
    thedir = "/proc/"
    dirs = [name for name in os.listdir(thedir) if os.path.isdir(os.path.join(thedir, name)) ]

    procs = []
    for name in dirs:
        if re.match("([0-9]+)", name):
            procs.append((name,thedir+name))

    return procs

def get_proc_socket_inodes(proc_path):
    path = proc_path+"/fd/"

    inodes = []
    for desc in os.listdir(path):
        target = os.readlink(path+desc)
        if "socket" in target:
            inodes.append(re.search(r"([0-9]+)", target).group(1))
        
    return inodes

def build_inode_to_pid_map():
    proc_dirs =  get_all_process_dirs()

    procs = []

    for pid, path in proc_dirs:
        print pid
        inodes = get_proc_socket_inodes(path)
        print "    " + inodes

        procs.append((pid,path,inodes))

    return procs


def get_pids_from_inode(inode, the_map):
    pids = []

    for p in the_map:
        if inode in p[2]:
            pids.append(p[0])

# uid as string
def get_username(uid):
    return pwd.getpwuid(int(uid))[0]
