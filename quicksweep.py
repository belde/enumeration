#!/usr/bin/python2
# Requires scapy and netaddr. Run as root.


import sys
import multiprocessing
import netaddr
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

def usage():
    print "quicksweep - a quick ICMP ping sweep tool"
    print
    print "Usage: quicksweep.py [network_IP_address]/[subnet]"
    print
    print "Make sure you run as root!"
    sys.exit(0)

def ping(jobq,resultsq):
    while True:
        target = jobq.get()
        if target is None:
            break
        if target == subnet.network:
            break
        if target == subnet.broadcast:
            break

        try:
            response = sr1(IP(dst=str(target))/ICMP(),timeout=2,verbose=0)
            if response:
                if response.ttl == 64:
                    target = str(target) + " Linux"
                    resultsq.put(target)
                elif response.ttl == 128:
                    target = target + " Windows"
                    resultsq.put(target)
                else:
                    resultsq.put(target)
        except:
            pass





if __name__ == '__main__':
    if len(sys.argv) == 1 or len(sys.argv) > 2:
        usage()

    # set target subnet
    subnet = netaddr.IPNetwork(sys.argv[1])

    sn_size = len(subnet)
    pool_size = sn_size

    jobs = multiprocessing.Queue()
    results = multiprocessing.Queue()

    pool = [multiprocessing.Process(target=ping, args=(jobs, results))
            for i in range(pool_size)]

    for p in pool:
        p.start()

    for target in subnet:
        jobs.put(str(target))

    for p in pool:
        jobs.put(None)

    for p in pool:
        p.join()

    while not results.empty():
        target = results.get()
        print(target)
