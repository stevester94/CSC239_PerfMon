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
from pymongo import MongoClient
import time
import zlib
import base64



pp = pprint.PrettyPrinter(indent=4)

mongo_client = MongoClient('localhost', 27017)
history  = mongo_client.historic_db.history
"""
history schema:
    <unix timestamp>
        { < all message types > : < corresponding data > }

"""


class Distiller:
    def __init__(self):
        self.prev_procs = None
        self.proc_payload = {} # Will be a dict of dicts with pid as primary key

        self.prev_disks = None
        self.disk_payload = {} # Will be a dict of dicts with disk as primary key

        self.system_payload = {} # system_payload is simple dict

        self.prev_cpu = None
        self.cpu_payload = {} # Will be a dict of dicts with disk as primary key

        self.prev_interrupts = None
        self.prev_context_switches = None

        self.prev_net_metrics = None
        # net_metrics are a simple dict of fields

        self.prev_nic_metrics = None

    # This function distills the procs into what will be used by the frontend
    # Will probably break this apart, but will serve as an example for now
    def distill_procs(self):

        desired_keys = [
            "interval_utilization",
            "physical_mem_KBytes",
            "username",
            "comm",
            "priority",
            "running_time",
            "virtual_mem_KBytes",
            "utime",
            "stime"
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
    def distill_disks(self, interval):
        disk_info = get_disk_info() # List of disks

        desired_keys = [
            "reads_completed",
            "sectors_read",
            "sectors_written",
            "writes_completed"
        ] # With disk name as primary key
        # and "percent_used"

        # First element is the key in the dict from disk.py, second is what its renamed to in payload
        second_desired_keys = [
            ("reads_completed", "reads_per_second"),
                # ("sectors_read", "sectors_read_per_second"),
                # ("sectors_written", "sectors_written_per_second"),
            ("writes_completed", "writes_per_second")
        ] # Still With disk name as primary key, all in the same overall dict

        self.disk_payload = {}
        disks_free_percent = get_disk_used_space()

        # Get standard snapshot info, and mix in percent free if possible
        for disk in disk_info:
            cur_disk_dict = {}

            for k in desired_keys:
                cur_disk_dict[k] = disk[k]

            for disk_free_info in disks_free_percent:
                if disk["name"] in disk_free_info[0]:
                    cur_disk_dict["percent_used"] = disk_free_info[1]
            # Check if we found one, if not just set it to 0
            if not "percent_used" in cur_disk_dict:
                cur_disk_dict["percent_used"] = 0

            self.disk_payload[disk["name"]] = cur_disk_dict
        
        # Get rate information if possible
        if self.prev_disks != None:
            rates = calc_disk_info_rates(self.prev_disks, disk_info, interval)
            for disk in rates:
                for k in second_desired_keys:
                    source_key = k[0]
                    transmuted_key = k[1]
                    self.disk_payload[disk["name"]][transmuted_key] = disk[source_key]
        # get percent free if possible


        
        self.prev_disks = disk_info
        return self.disk_payload


    def distill_system(self, interval):
        desired_keys = [
            "model",
            "clock_speed_MHz",
            "virtual_address_size_GB",
            "physical_address_size_GB",
            'free_kbytes',
            'total_kbytes',
            'used_percent',
            "context_switches",
            "interrupts",
            "uptime_secs",
            "arch"
        ]
        # And also, context_switches_per_second, interrupts_per_second

        mem_info = get_meminfo()
        interrupts = get_interrupts_serviced()
        context_switches = get_context_switches()

        # Just hijacking the mem_info dict for lazyness
        mem_info["context_switches"] = context_switches
        mem_info["interrupts"] = interrupts
        mem_info["uptime_secs"] = get_uptime()

        # Merge the dicts
        all_system_info = mem_info.copy()
        all_system_info.update(get_cpu_info())

        if self.prev_context_switches  != None:
            mem_info["context_switches_per_second"] = get_switches_per_second(self.prev_context_switches, context_switches, interval)
        if self.prev_interrupts != None:
            mem_info["interrupts_per_second"] = get_interrupts_per_second(self.prev_interrupts, interrupts, interval)

        payload = {}
        for key in desired_keys:
            payload[key] = all_system_info[key]
        
        self.prev_context_switches = context_switches
        self.prev_interrupts = interrupts

        self.system_payload = payload





        return payload

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
        net_metric_keys = ["ip_forwarding",
            "ip_in_receive",
            "ip_out_request",
            "tcp_active_opens",
            "tcp_current_established",
            "tcp_in_segs",
            "tcp_out_segs",
            "udp_in_datagram",
            "udp_out_datagram"
        ] # Net metric is simple dict

        # Input key, to be renamed to the second in tuple
        net_metric_rate_keys = [
            ("ip_forwarding", "ip_forwarding_per_second"),
            ("ip_in_receive", "ip_in_receive_per_second"),
            ("ip_out_request", "ip_out_request_per_second"),
            # ("tcp_active_opens", "tcp_active_opens_per_second"),
            # ("tcp_current_established", "tcp_current_established_per_second"),
            ("tcp_in_segs", "tcp_in_segs_per_second"),
            ("tcp_out_segs", "tcp_out_segs_per_second"),
            ("udp_in_datagram", "udp_in_datagram_per_second"),
            ("udp_out_datagram", "udp_out_datagram_per_second")
        ] # Net metric is simple dict

        nic_metric_keys = [
            "bytes_recvd",
            "packets_recvd",
            "bytes_sent",
            "packets_sent"
        ] # Each interface is entry in dict, each with above keys

        nic_metric_rate_keys = [
            ("bytes_recvd", "bytes_recvd_per_second"),
            # ("packets_recvd", "packets_recvd_per_second"),
            ("bytes_sent", "bytes_sent_per_second")
            # ("packets_sent", "packets_sent_per_second")
        ] # Each interface is entry in dict, each with above keys

        tcp_info_keys = [
            "local_address",
            "rem_address",
            "username",
            "program",
            "inode"
        ] # Dict for each socket, with above keys

        udp_info_keys = [
            "local_address",
            "rem_address",
            "username",
            "program",
            "inode"
        ] # Dict for each socket, with above keys


        net_metric_rates = None
        filtered_net_metric_rates = None
        net_metrics = None
        filtered_net_metrics = None

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
            for k in net_metric_rate_keys:
                filtered_net_metric_rates[k[1]] = net_metric_rates[k[0]]

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

        nic_metrics = get_nic_stats()
        nic_metrics_payload = {}
        for nic in nic_metrics:
            nic_dict = {}
            for k in nic_metric_keys:
                nic_dict[k] = nic_metrics[nic][k]
            nic_metrics_payload[nic_metrics[nic]["interface"]] = nic_dict
        
        nic_metrics_rates_payload = {}
        if self.prev_nic_metrics != None:
            nic_metrics_rates = calc_nic_rates(self.prev_nic_metrics, nic_metrics, interval)
            for nic in nic_metrics_rates:
                nic_dict = {}
                for k in nic_metric_rate_keys:
                    nic_dict[k[1]] = nic_metrics_rates[nic][k[0]]
                nic_metrics_rates_payload[nic] = nic_dict
        self.prev_nic_metrics = nic_metrics


        ret_dict = {}
        ret_dict["net_metric_rates"] = filtered_net_metric_rates
        ret_dict["tcp_info"] = filtered_tcp
        ret_dict["udp_info"] = filtered_udp
        ret_dict["net_metrics"] = filtered_net_metrics
        ret_dict["nic_metrics"] = nic_metrics_payload
        ret_dict["nic_metrics_rates"] = nic_metrics_rates_payload

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
        self.distiller.distill_disks(self.interval)
        self.distiller.distill_procs()
        self.distiller.distill_system(self.interval)
        self.distiller.distill_cpus()
        self.distiller.distill_network(self.interval)
    
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


        # COMPRESS THAT SHIT
        base64_compressed_payload = base64.b64encode(zlib.compress(json_payload, 9))
        print "Before compression payload size: " + str(len(json_payload))
        print "After compression payload size: " + str(len(base64_compressed_payload))



        sock = socket.socket(socket.AF_INET, # Internet
                            socket.SOCK_DGRAM) # UDP

        sock.sendto(base64_compressed_payload, (UDP_IP, UDP_PORT))

    def send_disks(self):
        payload = {}
        payload["msg_id"] = "msg_disks"
        payload["data"] = self.distiller.distill_disks(self.interval)

        self.send_payload(payload)
        self.mongo_payload[payload["msg_id"]] = payload["data"]


    def send_procs(self):
        payload = {}
        payload["msg_id"] = "msg_procs"
        payload["data"] = self.distiller.distill_procs()

        self.send_payload(payload)
        self.mongo_payload[payload["msg_id"]] = payload["data"]

        
    def send_system(self):
        payload = {}
        payload["msg_id"] = "msg_system"
        payload["data"] = self.distiller.distill_system(self.interval)

        self.send_payload(payload)
        self.mongo_payload[payload["msg_id"]] = payload["data"]


        
    def send_cpus(self):
        payload = {}
        payload["msg_id"] = "msg_cpus"
        payload["data"] = self.distiller.distill_cpus()

        self.send_payload(payload)
        self.mongo_payload[payload["msg_id"]] = payload["data"]


    def send_net(self):
        payload = {}
        payload["msg_id"] = "msg_net"
        payload["data"]   = self.distiller.distill_network(self.interval)

        self.send_payload(payload)
        self.mongo_payload[payload["msg_id"]] = payload["data"]


    def send_all(self):
        self.mongo_payload = {}
        self.send_disks()
        self.send_procs()
        self.send_system()
        self.send_cpus()
        self.send_net()

        # We batch them all like this so it's atomic
        # Eliminate 'unlikely' race condition where electron reads mid way through
        # a send_all
        history.find_one_and_update(
            {'timestamp': int(time.time())},
            {'$set': self.mongo_payload},
            upsert=True)

    def run(self):
        while True:
            sleep(self.interval)
            self.send_all()





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

    distiller.distill_disks(5)

    distiller.distill_procs()
    distiller.distill_procs()

    distiller.distill_system(5)

    distiller.distill_cpus()
    sleep(5)
    distiller.distill_cpus()

    # Print results
    pp.pprint(distiller.disk_payload)
    pp.pprint(distiller.proc_payload)
    pp.pprint(distiller.system_payload)
    pp.pprint(distiller.cpu_payload)

def distill_network():
    INTERVAL = 5
    distiller = Distiller()
    distiller.distill_network(INTERVAL)
    while True:
        sleep(INTERVAL)
        pp.pprint(distiller.distill_network(INTERVAL))
        # (distiller.distill_network(INTERVAL))



def distributor_test():
    distributor = Distributor(9001, 5) # port 9001, sleep time

    distributor.run()







if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "validate_procs": validate_procs()
        elif sys.argv[1] == "validate_meminfo": validate_meminfo()
        elif sys.argv[1] == "validate_context_switches": validate_context_switches()
        elif sys.argv[1] == "validate_interrupts_serviced": validate_interrupts_serviced()
        elif sys.argv[1] == "validate_disk_info": validate_disk_info()
        elif sys.argv[1] == "distiller_test": distiller_test()
        elif sys.argv[1] == "distill_network": distill_network()
    else: 
        distributor_test()
