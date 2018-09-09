#! /usr/bin/python
import re
from utils import *

import struct
import socket

# Thanks stackoverflow!
def translate_address_to_ipv4_string(input):
    addr_long = int(input, 16)
    hex(addr_long)
    struct.pack("<L", addr_long)
    return socket.inet_ntoa(struct.pack("<L", addr_long))

def parse_address_and_port(input):
    (address, port) = re.match(r"(.*):(.*)", input).groups()
    address = translate_address_to_ipv4_string(address)
    port = str(int(port, 16))

    try:
        address = socket.gethostbyaddr(address)[0]
    except:
        pass

    return (address, port)

def get_net_metrics():
    f = open("/proc/net/snmp")
    keys = ("ip_forwarding", "ip_in_receive", "ip_out_request", 
            "tcp_active_opens", "tcp_current_established", "tcp_in_segs", "tcp_out_segs", 
            "udp_in_datagram", "udp_out_datagram")
            # Relevant indices for each
            # 0 2 9 
            # 4 8 9 10
            # 0 3
    

    def do_the_thing(begining_str, tup_of_indices):
        lines = get_all_lines_start_matching(f, begining_str)
        line = lines[1]
        split_line = re.findall(r"([0-9]+)", line)
        stats = []
        for t in tup_of_indices:
            stats.append(split_line[t])
        return [int(stat) for stat in stats]

    ip_stats = do_the_thing("Ip:", (0,2,9))
    tcp_stats = do_the_thing("Tcp:", (4,8,9,10))
    udp_stats = do_the_thing("Udp:", (0,3))

    stats = ip_stats + tcp_stats + udp_stats
    d = dict(zip(keys, stats))


    if len(d) != len(keys):
        print len(d)
        print len(keys)
        raise ValueException

    return d


# There's gonna be garbage, oh well
def get_tcp_info():
    keys = ("username", "program", "sl", "local_address", "rem_address", "st", "tx_queue:rx_queue", 
            "tr:tm->when", "retrnsmt", "uid", "timeout", "inode")

    f = open("/proc/net/tcp")

    lines = search_all_lines_with_regex(f, r"\s*[0-9]+:")

    connections = []
    for index, l in enumerate(lines):
        only_data = re.search(r"\s*[0-9]+:\s*(.*)", l).group(1)
        separated_data = re.findall("\s*(\S*)\s*", only_data)
        try:
            separated_data.remove('')
        except e:
            pass
        separated_data = [index,] + separated_data

        # Translate raw hex addresses and ports into readable
        (host,port) = parse_address_and_port(separated_data[1])
        separated_data[1] = host+":"+port

        (host,port) = parse_address_and_port(separated_data[2])
        separated_data[2] = host+":"+port
        separated_data = ["USERNAME", "PROGRAM"] + separated_data 

        d = dict(zip(keys, separated_data))
        d["username"] = get_username(d["uid"])
        associated_pids = get_pids_from_inode(d["inode"], build_inode_to_pid_map())
        d["pids"] = associated_pids

        connections.append(d)


    return connections

def get_udp_info():
    keys = ("username", "program", "sl", "local_address", "rem_address", "st", "tx_queue:rx_queue", 
            "tr:tm->when", "retrnsmt", "uid", "timeout", "inode", "ref", "pointer", "drops")

    f = open("/proc/net/udp")

    lines = search_all_lines_with_regex(f, r"\s*[0-9]+:")

    connections = []
    for index, l in enumerate(lines):
        only_data = re.search(r"\s*[0-9]+:\s*(.*)", l).group(1)
        separated_data = re.findall("\s*(\S*)\s*", only_data)
        try:
            separated_data.remove('')
        except e:
            pass
        separated_data = [index,] + separated_data

        # Translate raw hex addresses and ports into readable
        (host,port) = parse_address_and_port(separated_data[1])
        separated_data[1] = host+":"+port

        (host,port) = parse_address_and_port(separated_data[2])
        separated_data[2] = host+":"+port

        separated_data = ["USERNAME", "PROGRAM"] + separated_data 

        d = dict(zip(keys, separated_data))
        d["username"] = get_username(d["uid"])
        associated_pids = get_pids_from_inode(d["inode"], build_inode_to_pid_map())
        d["pids"] = associated_pids
        connections.append(d)

    return connections




if __name__ == "__main__":
    print get_udp_info()
    print get_tcp_info()
    print get_overall_metrics()
