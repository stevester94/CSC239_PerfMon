#! /usr/bin/python
import re
from utils import *
from proc import *

import struct
import socket

hostname_cache = {
    "127.0.0.1": "localhost",
    "0.0.0.0"  : "localhost"
}

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

    # print address
    hostname = address
    if address in hostname_cache:
        hostname = hostname_cache[address]
        # print "hostname_cache hit: " + address + " -> " + hostname

    else:
        try:
            hostname = socket.gethostbyaddr(address)[0]
            hostname_cache[address] = hostname
            # print "hostname_cache miss: " + address + " -> " + hostname
        except:
            pass

    return (hostname, port)

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

def calc_net_interval_rate(prev,cur,interval):
    assert len(prev) == len(cur)

    interval_rates = {}
    for key,val in cur.iteritems():
        interval_rates[key] = float(cur[key] - prev[key])/interval

    return interval_rates


# There's gonna be garbage, oh well
def get_tcp_info():
    keys = ("username", "program", "sl", "local_address", "rem_address", "st", "tx_queue:rx_queue", 
            "tr:tm->when", "retrnsmt", "uid", "timeout", "inode", "procs")

    f = open("/proc/net/tcp")

    lines = search_all_lines_with_regex(f, r"\s*[0-9]+:")

    connections = []
    dictified_procs = dictify_procs(get_all_complete_procs()) # Compute only once
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

        associated_procs = get_procs_from_inode(d["inode"], dictified_procs)
        d["procs"] = associated_procs
        if len(associated_procs) > 0:
            d["program"] = associated_procs[0]["comm"]
        else:
            d["program"] = "none"

        connections.append(d)


    return connections

def get_udp_info():
    keys = ("username", "sl", "local_address", "rem_address", "st", "tx_queue:rx_queue", 
            "tr:tm->when", "retrnsmt", "uid", "timeout", "inode", "ref", "pointer", "drops")

    f = open("/proc/net/udp")

    lines = search_all_lines_with_regex(f, r"\s*[0-9]+:")

    connections = []
    dictified_procs = dictify_procs(get_all_complete_procs())

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

        separated_data = ["USERNAME",] + separated_data 

        d = dict(zip(keys, separated_data))
        d["username"] = get_username(d["uid"])
        associated_procs = get_procs_from_inode(d["inode"], dictified_procs)
        d["procs"] = associated_procs
        if len(associated_procs) > 0:
            d["program"] = associated_procs[0]["comm"]
        else:
            d["program"] = "none"
        connections.append(d)

    return connections


def get_nic_stats():
    keys = [
        "MBytes_recvd",
        "packets_recvd",
        "errs_recvd",
        "drop_recvd",
        "fifo_recvd",
        "frame_recvd",
        "compressed_recvd",
        "multicast_revd",
        "MBytes_sent",
        "packets_sent",
        "errs_sent",
        "drop_sent",
        "fifo_sent",
        "colls_sent",
        "carrier_sent",
        "compressed_sent"
    ] # With "interface" as primary key


    f = open("/proc/net/dev")

    # First two lines are junk
    f.readline()
    f.readline()

    nics = {}
    for line in f.readlines():
        split_line = line.split()
        nic_dict =  {}
        nic_dict["interface"] = split_line[0]
        for index,key in enumerate(keys):
            nic_dict[key] = int(split_line[index+1]) # Ofset because first split is the interface name

        # Convert bytes to MBytes
        nic_dict["MBytes_recvd"] = float(nic_dict["MBytes_recvd"]) / 2**20
        nic_dict["MBytes_sent"]  = float(nic_dict["MBytes_sent"])  / 2**20

        nics[split_line[0]] = nic_dict



    return nics

def calc_nic_rates(prev_nics, current_nics, interval_secs):

    keys = [
        "MBytes_recvd",
        "packets_recvd",
        "errs_recvd",
        "drop_recvd",
        "fifo_recvd",
        "frame_recvd",
        "compressed_recvd",
        "multicast_revd",
        "MBytes_sent",
        "packets_sent",
        "errs_sent",
        "drop_sent",
        "fifo_sent",
        "colls_sent",
        "carrier_sent",
        "compressed_sent"
    ] # With 'interface' as primary key

    nic_rates = {}
    for nic, _ in current_nics.iteritems():
        rate_dict = {}
        for k in keys:
            rate_dict[k] = (current_nics[nic][k] - prev_nics[nic][k]) / interval_secs
        nic_rates[nic] = rate_dict
    
    return nic_rates


def calc_nic_speed(nic_name):
    p = Popen(['ethtool', nic_name], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    response, err = p.communicate() # This gives MBits per second

    match = re.search("Speed: ([0-9]*)", response)

    if match:
        mbits_per_sec = float(match.group(1))
        return mbits_per_sec / 8.0 # Megabytes per second
    else:
        return -1


if __name__ == "__main__":
    print calc_nic_speed("lo:")
