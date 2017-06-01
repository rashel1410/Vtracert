#!/usr/bin/python
""" Textual Tracert """
## @file TextTracert.py The textual tracert program

import argparse
import os
import random
import traceback
import urlparse
import my_tracert
import sys

from common import constants
from common import util

## Parsing
# returns program's arguments
#
def parse_args():
    """Parse program argument."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--address',
        help='ip address or dns(name of site)',
    )
    parser.add_argument(
        '--mac',
        default='GET_MAC',
        help='MAC address of your compute, without - separation',
    )
    
    args = parser.parse_args()
    return args
    
## Textual tracert
#@ param dest (string) - address to trace
#
# Prints to the screen a serial num of the hop and the ip address
#
def TextTracert(dest,src_mac):
    
    ttl = 1
    t=5
    hop = ''
    MAX_HOPS = 30
    status = 'NONE'
    sys.stderr.write('\n  Tracing route to %s \n  over a maximum of %s hops:\n' %(dest, MAX_HOPS))
    while status != 'REACH' and ttl < MAX_HOPS:
    
        status,hop = my_tracert.my_tracert(dest,ttl,t,src_mac)
        if status == "TIMEOUT":
            sys.stderr.write('  '+str(ttl)+'\t')
            sys.stderr.write('\t*\n')
        else:
            ip = ''
            index = 0
            part = ''
            for i in range(len(hop)/2):
                part = hop[index:index+2]
                ip += str(int(part,16))+'.'
                index += 2
            ip = ip[:-1]
            sys.stderr.write('  '+str(ttl)+'\t')
            sys.stderr.write(ip+'\n')
        ttl += 1
    if status=='REACH':
        sys.stderr.write('Trace complete. The packet reached the destination!\n')
    else:
        sys.stderr.write('Tracert timed out - max %s hops\n' %MAX_HOPS)
        
        
## main
#
def main():
    args = parse_args()
    TextTracert(args.address,args.mac)
    
if __name__ == '__main__':
    main()
    