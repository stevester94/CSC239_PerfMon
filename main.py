#! /usr/bin/python

from network import *
from system import *
from disk import *
import pprint
from time import sleep
from proc import *


# if __name__ == "__main__":
#     pp = pprint.PrettyPrinter(indent=4)

#     prev_net_metrics = None
#     prev_cpu_utilization = None
#     prev_self_metrics = None
#     prev_meminfo = None
#     prev_context_switches = None
#     prev_interrupts_serviced = None

#     while True:

#         print "get_net_metrics()"

#         net_metrics = get_net_metrics()
#         pp.pprint(net_metrics)
#         print "=================================================================================="


#         print "get_tcp_info()"
#         tcp_info = get_tcp_info()
#         pp.pprint(tcp_info)
#         print "=================================================================================="


#         print "get_udp_info()"
#         udp_info = get_udp_info()
#         pp.pprint(udp_info)
#         print "=================================================================================="


#         print "get_cpu_utilization()"
#         cpu_utilization = get_cpu_utilization()
#         pp.pprint(cpu_utilization)
#         print "=================================================================================="


#         print "get_process_metrics(self)"
#         self_metrics = get_process_metrics("self")
#         pp.pprint(self_metrics)
#         print "=================================================================================="


#         print "get_meminfo()"
#         meminfo = get_meminfo()
#         pp.pprint(meminfo)
#         print "=================================================================================="


#         print "get_context_switches()"
#         context_switches = get_context_switches()
#         pp.pprint(context_switches)
#         print "=================================================================================="


#         print "get_interrupts_serviced()"
#         interrupts_serviced = get_interrupts_serviced()
#         pp.pprint(interrupts_serviced)
#         print "=================================================================================="


#         print "get_disk_reads()"
#         disk_reads = get_disk_reads()
#         pp.pprint(disk_reads)
#         print "=================================================================================="

#         SLEEP_TIME = 5
#         if prev_net_metrics != None:
#             # tcp_in_segs
#             print "tcp_in_segs_rate: %f" % (float(net_metrics["tcp_in_segs"] - prev_net_metrics["tcp_in_segs"])/SLEEP_TIME)
#             print "tcp_out_segs_rate: %f" % (float(net_metrics["tcp_out_segs"] - prev_net_metrics["tcp_out_segs"])/SLEEP_TIME)
#             print "udp_in_datagram_rate: %f" % (float(net_metrics["udp_in_datagram"] - prev_net_metrics["udp_in_datagram"])/SLEEP_TIME)
#             print "udp_out_datagram_rate: %f" % (float(net_metrics["udp_out_datagram"] - prev_net_metrics["udp_out_datagram"])/SLEEP_TIME)
#             print "context_switches_rate: %f" % (float(context_switches - prev_context_switches)/SLEEP_TIME)
#             print "interrupts_serviced_rate: %f" % (float(interrupts_serviced - prev_interrupts_serviced)/SLEEP_TIME)
#         prev_net_metrics = net_metrics
#         prev_cpu_utilization = cpu_utilization
#         prev_self_metrics = self_metrics
#         prev_meminfo = meminfo
#         prev_context_switches = context_switches
#         prev_interrupts_serviced = interrupts_serviced


#         sleep(SLEEP_TIME)


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)

    prev_cpus = None
    prev_pid  = None
    while True:
        cpus = get_cpu_utilization()
        proc = get_proc_complete("4174")
        # pp.pprint(cpus)

        if prev_cpus != None:
            print calc_percent_time_busy(prev_cpus, cpus)
            print calc_proc_utilization_interval_percent(prev_proc, proc)

        prev_proc = proc
        prev_cpus = cpus
        print "========================================="
        sleep(5)