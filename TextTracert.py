#!/usr/bin/python

import argparse
import base64
import Cookie
import contextlib
import datetime
import errno
import os
import random
import socket
import traceback
import urlparse
import my_tracert

from common import constants
from common import util

## Parsing
#@ no params
#@ returns program's arguments
def parse_args():
    """Parse program argument."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--address',
        help='ip address or dns(name of site)',
    )
    args = parser.parse_args()
    return args
    
def main():
    
    args = parse_args()
    print args
    ttl = 1
    args = []
    t=5
    hop = ''
    MAX_HOPS = 20
    status = 'NONE'
    while status!='REACH' and ttl<MAX_HOPS:
     
        status,hop = my_tracert.my_tracert(args.address,ttl,t)
        ip = ''
        index = 0
        part = ''
        for i in range(len(hop)/2):
            part = hop[index:index+2]
            ip += str(int(part,16))+'.'
            index += 2
        ip = ip[:-1]
        sys.stderr.write(str(ttl)+'\t')
        sys.stderr.write(ip+'\n')
        ttl += 1
    if status=='REACH':
        sys.stderr.write('Trace complete. The packet reached the destination!')
    else:
        sys.stderr.write('Tracert timed out - max %s hops\n' %MAX_HOPS)
    
if __name__ == '__main__':
    main()
    
#01110011-01101000-01100001-01100010-01100001-01101011
#101001 10110100 00110000 101100010 01100001 01101011