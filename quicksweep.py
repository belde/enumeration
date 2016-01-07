#!/usr/bin/python2
# Requires scapy and netaddr. Run as root.

import argparse
import sys
import multiprocessing
import netaddr
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

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
                if args.os_detect:
                    if response.ttl == 64:
                        target = str(target) + " Linux"
                        resultsq.put(target)
                    elif response.ttl == 128:
                        target = target + " Windows"
                        resultsq.put(target)
                    else:
                        resultsq.put(target)
                else:
                    resultsq.put(target)

        except:
            pass





if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("network",type=str,help="[network_address]/[subnet]")
    parser.add_argument("-o","--os_detect",help="simple os detection",action="store_true")
    args = parser.parse_args()

    subnet = netaddr.IPNetwork(args.network)

    pool_size = len(subnet)
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
