#! /usr/bin/python
import re
from utils import *

def get_overall_metrics():
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

    return dict(zip(keys, stats))




if __name__ == "__main__":
    print get_overall_metrics()

