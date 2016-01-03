#!/usr/bin/python2
# Requires scapy and netaddr. Run as root.
# This script will run a simple TCP SYN sweep against ports 80 and 443 import sys

import sys
import multiprocessing
import netaddr
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

def usage():
    print "tcpsweep - a quick TCP SYN sweep tool"
    print
    print "Usage: tcpsweep.py [network_IP_address]/[subnet]"
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
            response = sr1(IP(dst=str(target))/TCP(sport=RandShort(),dport=[80,443],flags="S"),timeout=2,verbose=0)
            if response:
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
