#! /usr/bin/python

import os
import re
import pwd
import sys

CLOCK_PER_SECOND = 100

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

# uid as string
def get_username(uid):
    return pwd.getpwuid(int(uid))[0]


def get_uptime_clocks():
    keys = ("uptime", "idletime")
    f = open("/proc/uptime")

    line = f.read()
    return dict(zip(keys, [float(f)*CLOCK_PER_SECOND for f in re.search("(.*?) (.*)", line).groups()]))

