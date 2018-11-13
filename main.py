#! /usr/bin/python

from network import *
from system import *
from disk import *
import pprint
from time import sleep
from proc import *
import sys
import json


def rate_demo():
    pp = pprint.PrettyPrinter(indent=4)

    prev_net_metrics = None
    prev_self_metrics = None
    prev_meminfo = None
    prev_context_switches = None
    prev_interrupts_serviced = None
    prev_disk_info = None

    while True:

        print "get_net_metrics()"

        net_metrics = get_net_metrics()
        pp.pprint(net_metrics)
        print "=================================================================================="


        print "get_tcp_info()"
        tcp_info = get_tcp_info()
        pp.pprint(tcp_info)
        print "=================================================================================="


        print "get_udp_info()"
        udp_info = get_udp_info()
        pp.pprint(udp_info)
        print "=================================================================================="


        print "get_meminfo()"
        meminfo = get_meminfo()
        pp.pprint(meminfo)
        print "=================================================================================="


        print "get_context_switches()"
        context_switches = get_context_switches()
        pp.pprint(context_switches)
        print "=================================================================================="


        print "get_interrupts_serviced()"
        interrupts_serviced = get_interrupts_serviced()
        pp.pprint(interrupts_serviced)
        print "=================================================================================="


        print "get_disk_info()"
        disk_info = get_disk_info()
        pp.pprint(disk_info)
        print "=================================================================================="

        SLEEP_TIME = 5
        if prev_net_metrics != None:
            print "Hand Calc'd"
            print "tcp_in_segs_rate: %f" % (float(net_metrics["tcp_in_segs"] - prev_net_metrics["tcp_in_segs"])/SLEEP_TIME)
            print "tcp_out_segs_rate: %f" % (float(net_metrics["tcp_out_segs"] - prev_net_metrics["tcp_out_segs"])/SLEEP_TIME)
            print "udp_in_datagram_rate: %f" % (float(net_metrics["udp_in_datagram"] - prev_net_metrics["udp_in_datagram"])/SLEEP_TIME)
            print "udp_out_datagram_rate: %f" % (float(net_metrics["udp_out_datagram"] - prev_net_metrics["udp_out_datagram"])/SLEEP_TIME)
            print "context_switches_rate: %f" % (float(context_switches - prev_context_switches)/SLEEP_TIME)
            print "interrupts_serviced_rate: %f" % (float(interrupts_serviced - prev_interrupts_serviced)/SLEEP_TIME)

            print "Interface calc'd"
            print calc_net_interval_rate(prev_net_metrics, net_metrics, SLEEP_TIME)
            pp.pprint(calc_disk_info_rates(prev_disk_info, disk_info, SLEEP_TIME))
        prev_net_metrics = net_metrics
        prev_meminfo = meminfo
        prev_context_switches = context_switches
        prev_interrupts_serviced = interrupts_serviced
        prev_disk_info = disk_info


        sleep(SLEEP_TIME)


def top_demo():
    pp = pprint.PrettyPrinter(indent=4)

    # top mode
    prev_cpus = None
    prev_procs  = None
    while True:
        cpus = get_cpu_utilization()
        procs = dictify_procs(get_all_complete_procs())


        if prev_cpus != None:
            populate_all_proc_utilization_interval_percent(prev_procs, procs)

            print "CPU usage:"
            for cpu in calc_percent_time_busy(prev_cpus, cpus):
                print "%s: %s%% busy" % cpu
            print 

            print "Memory Usage"
            print " ".join([ key+": "+str(val) for (key,val) in get_meminfo().iteritems()])
            print

            print "Top 10 processes by utilization:"
            print " ".join(("username", "comm", "virtual_mem_bytes", "physical_mem_pages", "interval_utilization"))
            for (pid, _) in sort_procs_by_interval_utilization(procs)[:10]:
                print " ".join(get_proc_highlights(procs[pid]))
            print


        prev_procs = procs
        prev_cpus = cpus
        print "========================================="
        sleep(5)


# OK this is getting out of hand
# Going to verify that the keys in each proc does not change
def procs_validation():
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


# This function distills the procs into what will be used by the frontend
# Will probably break this apart, but will serve as an example for now
def distill_procs():
    prev_procs = None
    pp = pprint.PrettyPrinter(indent=4)
    SLEEP_TIME = 1


    desired_keys = [
        "interval_utilization",
        "physical_mem_bytes",
        "username",
        "comm",
        "priority",
        "utime"
    ] # And will have 'pid', embedded in the for loop

    while True:
        procs = dictify_procs(get_all_complete_procs())
        if prev_procs != None:
            populate_all_proc_utilization_interval_percent(prev_procs, procs)
            proc_payload = [] # Will be an array of dicts

            for key,value in procs.iteritems():
                this_proc = {}
                this_proc["pid"] = key
                for desired in desired_keys:
                    this_proc[desired] = value[desired]
                proc_payload.append(this_proc)

            f = open("sample_procs.json", "w")
            f.write(json.dumps(proc_payload))
            f.close()
            print "Great success, exiting"
            exit(0)


                

        prev_procs = procs
        sleep(SLEEP_TIME)



def vomit_demo():
    pp = pprint.PrettyPrinter(indent=4)

    # prev_net_metrics = None
    prev_self_metrics = None
    prev_meminfo = None
    prev_context_switches = None
    prev_interrupts_serviced = None
    prev_disk_info = None
    prev_cpus = None
    prev_procs  = None

    while True:
        # Net metrics needs work, too slow
        # print "get_net_metrics()"

        # net_metrics = get_net_metrics()
        # pp.pprint(net_metrics)
        # print "=================================================================================="


        # print "get_tcp_info()"
        # tcp_info = get_tcp_info()
        # pp.pprint(tcp_info)
        # print "=================================================================================="


        # print "get_udp_info()"
        # udp_info = get_udp_info()
        # pp.pprint(udp_info)
        # print "=================================================================================="


        print "get_meminfo()"
        meminfo = get_meminfo()
        pp.pprint(meminfo)
        print "=================================================================================="


        print "get_context_switches()"
        context_switches = get_context_switches()
        pp.pprint(context_switches)
        print "=================================================================================="


        print "get_interrupts_serviced()"
        interrupts_serviced = get_interrupts_serviced()
        pp.pprint(interrupts_serviced)
        print "=================================================================================="


        print "get_disk_info()"
        disk_info = get_disk_info()
        pp.pprint(disk_info)
        print "=================================================================================="




        procs = dictify_procs(get_all_complete_procs())
        cpus = get_cpu_utilization()


        SLEEP_TIME = 5
        if prev_procs != None:
            # print "Network interval rate:"
            # pp.pprint(calc_net_interval_rate(prev_net_metrics, net_metrics, SLEEP_TIME))
            # print "=================================================================================="

            print "Disk info rates"
            pp.pprint(calc_disk_info_rates(prev_disk_info, disk_info, SLEEP_TIME))
            print "=================================================================================="

            print "get_all_complete_procs(), dictified, utilization, first entry"
            procs = dictify_procs(get_all_complete_procs())
            populate_all_proc_utilization_interval_percent(prev_procs, procs)
            pp.pprint(procs.itervalues().next())
            print "=================================================================================="

            f = open("sample_procs.json", "w")
            f.write(json.dumps(procs))
            exit(0)

            print "get_cpu_utilization()"
            cpus = get_cpu_utilization()
            pp.pprint(cpus)

            print "CPU usage (interval):"
            for cpu in calc_percent_time_busy(prev_cpus, cpus):
                print "%s: %s%% busy" % cpu
            print "=================================================================================="



        # prev_net_metrics = net_metrics
        prev_meminfo = meminfo
        prev_context_switches = context_switches
        prev_interrupts_serviced = interrupts_serviced
        prev_disk_info = disk_info
        prev_procs = procs
        prev_cpus = cpus


        sleep(SLEEP_TIME)



if __name__ == "__main__":
    if sys.argv[1] == "top": top_demo()
    if sys.argv[1] == "rates": rate_demo()
    if sys.argv[1] == "vomit": vomit_demo()
    if sys.argv[1] == "procs_prep": procs_validation()
    if sys.argv[1] == "distill_procs": distill_procs()