#! /usr/bin/python

from network import *
from system import *
from disk import *
import pprint
from time import sleep
from proc import *
import sys
import json
import socket
import threading


pp = pprint.PrettyPrinter(indent=4)


class Distiller:
    def __init__(self):
        self.prev_procs = None
        self.proc_payload = {} # Will be a dict of dicts with pid as primary key

        self.prev_disks = None
        self.disk_payload = {} # Will be a dict of dicts with disk as primary key

        self.system_payload = {}

        self.prev_cpu = None
        self.cpu_payload = {} # Will be a dict of dicts with disk as primary key

        self.prev_net_metrics = None




    # This function distills the procs into what will be used by the frontend
    # Will probably break this apart, but will serve as an example for now
    def distill_procs(self):

        desired_keys = [
            "interval_utilization",
            "physical_mem_bytes",
            "username",
            "comm",
            "priority",
            "utime"
        ] # With pid as the primary key

        procs = dictify_procs(get_all_complete_procs())
        if self.prev_procs != None:
            populate_all_proc_utilization_interval_percent(self.prev_procs, procs)

            self.proc_payload = {}# Clear if we have anything already

            for pid,value in procs.iteritems():
                this_proc = {}
                for desired in desired_keys:
                    this_proc[desired] = value[desired]
                self.proc_payload[pid] = this_proc

        self.prev_procs = procs
        return self.proc_payload
    

    # disk reads, block reads, disk writes, blocks written
    def distill_disks(self):
        disk_info = get_disk_info() # List of disks

        desired_keys = [
            "reads_completed",
            "sectors_read",
            "sectors_written",
            "writes_completed"
        ] # With disk name as primary key

        self.disk_payload = {}


        for disk in disk_info:
            cur_disk_dict = {}

            for k in desired_keys:
                cur_disk_dict[k] = disk[k]
            self.disk_payload[disk["name"]] = cur_disk_dict
        return self.disk_payload


    def distill_system(self):
        desired_keys = [
            'free_kbytes',
            'total_kbytes',
            'used_percent',
            "context_switches",
            "interrupts",
            "uptime_secs"
        ]

        mem_info = get_meminfo()
        interrupts = get_interrupts_serviced()
        context_switches = get_context_switches()

        # Just hijacking the mem_info dict for lazyness
        mem_info["context_switches"] = context_switches
        mem_info["interrupts"] = interrupts
        mem_info["uptime_secs"] = get_uptime()

        self.system_payload = mem_info
        return self.system_payload

    def distill_cpus(self):
        desired_keys = [
            "system_mode_ms",
            "user_mode_ms"
        ] # and interval_utilization, cpu_name as the primary key
        cur_cpu = get_cpu_utilization()

        if self.prev_cpu != None:
            self.cpu_payload = {}

            # Just init the cpu_name primary keys
            for cpu in cur_cpu:
                self.cpu_payload[cpu["cpu_name"]] = {}
            
            for cpu in cur_cpu:
                for key in desired_keys:
                    self.cpu_payload[cpu["cpu_name"]][key] = cpu[key]

            percents = calc_percent_time_busy(self.prev_cpu, cur_cpu)
            for cpu in percents:
                self.cpu_payload[cpu[0]]["interval_utilization"] = cpu[1]

        self.prev_cpu = cur_cpu
        return self.cpu_payload

    def distill_network(self, interval):
        net_metric_keys = ["ip_forwarding", "ip_in_receive", "ip_out_request", 
                "tcp_active_opens", "tcp_current_established", "tcp_in_segs", "tcp_out_segs", 
                "udp_in_datagram", "udp_out_datagram"]

        tcp_info_keys = [
            "local_address",
            "rem_address",
            "username",
            "program"
        ]

        udp_info_keys = [
            "local_address",
            "rem_address",
            "username",
            "program",
            "inode"
        ]


        net_metric_rates = None
        filtered_net_metric_rates = None
        net_metrics = None
        filtered_net_metrics = None

        print "get_net_metrics()"
        # Calc metric interval if applicable
        net_metrics = get_net_metrics()
        if self.prev_net_metrics != None:
            net_metric_rates = calc_net_interval_rate(self.prev_net_metrics, net_metrics, interval)
        self.prev_net_metrics = net_metrics

        # Get only the keys we want
        filtered_net_metrics = {}
        for k in net_metric_keys:
            filtered_net_metrics[k] = net_metrics[k]
        
        # Do the same if we have the rate based data
        if net_metric_rates != None:
            filtered_net_metric_rates = {}
            for k in net_metric_keys:
                filtered_net_metric_rates[k] = net_metric_rates[k]

        # OK, so there _can_ be multiple processes that write to the same inode (socket), but that is 
        # not common.
        filtered_tcp = []
        tcp_info = get_tcp_info()
        for tcp in tcp_info:
            socket_dict = {}
            for k in tcp_info_keys:
                socket_dict[k] = tcp[k]
            filtered_tcp.append(socket_dict)

        # print "=================================================================================="


        udp_info = get_udp_info()
        filtered_udp = []
        for udp in udp_info:
            socket_dict = {}
            for k in udp_info_keys:
                socket_dict[k] = udp[k]
            filtered_udp.append(socket_dict)
        # print "=================================================================================="

        ret_dict = {}
        ret_dict["net_metric_rates"] = filtered_net_metric_rates
        ret_dict["tcp_info"] = filtered_tcp
        ret_dict["udp_info"] = filtered_udp
        ret_dict["net_metrics"] = filtered_net_metrics

        return ret_dict


class Distributor(threading.Thread):
    def __init__(self, port, interval):
        # self.super()
        self.valid_msgs = [
            "msg_disks",
            "msg_procs",
            "msg_system",
            "msg_cpus",
            "msg_net"
        ]

        self.port = port
        self.interval = interval
        self.distiller = Distiller()

        # Prime the pump
        self.distiller.distill_disks()
        self.distiller.distill_procs()
        self.distiller.distill_system()
        self.distiller.distill_cpus()
    
    # Will jsonify, payload must be a dict of {msg_id, data}
    def send_payload(self, payload):
        if payload["msg_id"] not in self.valid_msgs:
            print "msg_id: ", payload.msg_id, " is not valid"
            sys.exit(1)

        json_payload = json.dumps(payload)
        UDP_IP = "127.0.0.1"
        UDP_PORT = self.port
        print "UDP target IP:", UDP_IP
        print "UDP target port:", UDP_PORT

        print "Sending payload:", json_payload 
        sock = socket.socket(socket.AF_INET, # Internet
                            socket.SOCK_DGRAM) # UDP

        sock.sendto(json_payload, (UDP_IP, UDP_PORT))

    def send_disks(self):
        payload = {}
        payload["msg_id"] = "msg_disks"
        payload["data"] = self.distiller.distill_disks()
        self.send_payload(payload)

    def send_procs(self):
        payload = {}
        payload["msg_id"] = "msg_procs"
        payload["data"] = self.distiller.distill_procs()
        self.send_payload(payload)
        
    def send_system(self):
        payload = {}
        payload["msg_id"] = "msg_system"
        payload["data"] = self.distiller.distill_system()
        self.send_payload(payload)
        
    def send_cpus(self):
        payload = {}
        payload["msg_id"] = "msg_cpus"
        payload["data"] = self.distiller.distill_cpus()
        self.send_payload(payload)

    def send_net(self):
        payload = {}
        payload["msg_id"] = "msg_net"
        payload["data"]   = self.distiller.distill_network(self.interval)
        self.send_payload(payload)

    def send_all(self):
        self.send_disks()
        self.send_procs()
        self.send_system()
        self.send_cpus()
        self.send_net()

    def run(self):
        while True:
            self.send_all()
            sleep(self.interval)





###################
# Validation code #
###################

def are_keys_same_as_last(previous_dict, current_dict):
    return set(previous_dict.keys()) == set(current_dict.keys())

def validate_meminfo():
    pp = pprint.PrettyPrinter(indent=4)
    prev_meminfo = None
    SLEEP_TIME = 1

    while True:
        if prev_meminfo != None:
            cur_meminfo = get_meminfo()
            print "Keys are the same?: " +  str(are_keys_same_as_last(prev_meminfo, cur_meminfo))
        prev_meminfo = get_meminfo()
        sleep(SLEEP_TIME)

#Literally just an int
def validate_context_switches():
    pp = pprint.PrettyPrinter(indent=4)
    SLEEP_TIME = 1

    while True:
        pp.pprint(get_context_switches())
        sleep(SLEEP_TIME)

def validate_interrupts_serviced():
    pp = pprint.PrettyPrinter(indent=4)
    SLEEP_TIME = 1

    while True:
        pp.pprint(get_interrupts_serviced())
        sleep(SLEEP_TIME)

# Use as a template for checking other keys
# def validate_disk_info():
#     pp = pprint.PrettyPrinter(indent=4)
#     prev = None
#     SLEEP_TIME = 1

#     while True:
#         cur = get_disk_info()
#         if prev != None:
#             print "Keys are the same?: " +  str(are_keys_same_as_last(prev, cur))
#         prev = cur
#         sleep(SLEEP_TIME)

def validate_disk_info():
    pp = pprint.PrettyPrinter(indent=4)
    prev_keys = None
    SLEEP_TIME = 1

    while True:
        disk_info = get_disk_info()
        for d in disk_info:
            keys = set(d.keys())
            if keys != set(disk_info[0]):
                print "Keys in current set do not match"
                pp.pprint(keys)
                pp.pprint(set(disk_info[0]))
                return
        
            if prev_keys != None:
                if keys != prev_keys:
                    print "Keys in current set do not match previous"
                    pp.pprint(keys)
                    pp.pprint(prev_keys)
                    return
        print "Keys match"
        prev_keys = set(disk_info[0].keys())
        sleep(SLEEP_TIME)

# OK this is getting out of hand
# Going to verify that the keys in each proc does not change
def validate_procs():
    prev_procs = None
    pp = pprint.PrettyPrinter(indent=4)
    SLEEP_TIME = 1

    while True:
        procs = dictify_procs(get_all_complete_procs())
        if prev_procs != None:
            populate_all_proc_utilization_interval_percent(prev_procs, procs)
            last_keys_set = None
            for proc in procs.itervalues():
                if last_keys_set != None:
                    if set(proc.keys()) != last_keys_set:
                        print "Keys are not equivalent :("
                        exit(1)
                    else:
                        print set(proc.keys())
                last_keys_set = set(proc.keys())

        prev_procs = procs
        sleep(SLEEP_TIME)

def distiller_test():
    distiller = Distiller()

    distiller.distill_disks()

    distiller.distill_procs()
    distiller.distill_procs()

    distiller.distill_system()

    distiller.distill_cpus()
    sleep(5)
    distiller.distill_cpus()

    # Print results
    pp.pprint(distiller.disk_payload)
    pp.pprint(distiller.proc_payload)
    pp.pprint(distiller.system_payload)
    pp.pprint(distiller.cpu_payload)

def distill_network():
    distiller = Distiller()
    while True:
        pp.pprint(distiller.distill_network(5))
        sleep(5)
        pp.pprint(distiller.distill_network(5))



def distributor_test():
    distributor = Distributor(9001, 1) # port 9001, sleep time

    distributor.run()







if __name__ == "__main__":
    if sys.argv[1] == "validate_procs": validate_procs()
    if sys.argv[1] == "validate_meminfo": validate_meminfo()
    if sys.argv[1] == "validate_context_switches": validate_context_switches()
    if sys.argv[1] == "validate_interrupts_serviced": validate_interrupts_serviced()
    if sys.argv[1] == "validate_disk_info": validate_disk_info()
    if sys.argv[1] == "distiller_test": distiller_test()
    if sys.argv[1] == "distributor_test": distributor_test()
    if sys.argv[1] == "distill_network": distill_network()
