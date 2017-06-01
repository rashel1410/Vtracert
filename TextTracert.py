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
    parser.add_argument(
        '--debug',
        default='DONT',
        help='--debug D, if you want to see the debug prints in a file in VTracert',
    )
    
    args = parser.parse_args()
    return args
    
## Textual tracert
#@ param dest (string) - address to trace
#
# Prints to the screen a serial num of the hop and the ip address
#
def TextTracert(dest,src_mac,debug):
    
    if debug == 'D':
        to_file = True
    else:
        to_file = False
    ttl = 1
    t=5
    hop = ''
    MAX_HOPS = 30
    status = 'NONE'
    time_out = 0
    sys.stderr.write('\n  Tracing route to %s \n  over a maximum of %s hops:\n\n' %(dest, MAX_HOPS))
    while status != 'REACH' and ttl < MAX_HOPS:
    
        status,hop,time_out = my_tracert.my_tracert(dest,ttl,t,src_mac,time_out,to_file)
        if status == "TIMEOUT":
            sys.stderr.write('  %s\t' %str(ttl))
            sys.stderr.write('\t*\tRequest timed out.\n')
        else:
            ip = ''
            index = 0
            part = ''
            for i in range(len(hop)/2):
                part = hop[index:index+2]
                ip += str(int(part,16))+'.'
                index += 2
            ip = ip[:-1]
            sys.stderr.write('  %s\t' %str(ttl))
            sys.stderr.write('%s\t%s ms\n' %(ip,str(time_out)))
        ttl += 1
    if status=='REACH':
        sys.stderr.write('Trace complete. The packet reached the destination!\n')
    else:
        sys.stderr.write('Tracert timed out - max %s hops\n' %MAX_HOPS)
        
        
## main
#
def main():
    args = parse_args()
    TextTracert(args.address,args.mac,args.debug)
    
if __name__ == '__main__':
    main()
