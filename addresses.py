#!/usr/bin/python
""" gives ip addresses """
## @file addresses.py Uses sockets to find out the ip addresses

import socket
import struct

## my ip address
# returns my ip address
#
def my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    #print IP
    IP = IP.split('.')
    ip = ''
    for part in IP:
        ip += "%02x" %int(part)
    return ip

## ip of a given address
#@ param name (string) - name of a site
# returns the ip address of the site
#
def address_ip(name):
    addr = socket.gethostbyname(name)
    addr = addr.split('.')
    ip = ''
    for part in addr:
        ip += "%02x" %int(part)
    return ip
