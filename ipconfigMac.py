#!/usr/bin/python
""" gives mac addresses """
## @file ipconfigMac.py Uses subprocess and ipconficMac to return mac addresses

import addresses
import subprocess

from common import constants

## ipconfig/all
# returns an output of ipconfig/all running
#
# Runs ipconfig/all using subprocess
#
def ipconfig_all():

    args = ["ipconfig", "/all"]
    proc = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE)
    data = proc.stdout.read()
    lines = data.split('\r\n')
    return lines
    
## Source mac
# returns the mac address of the computer
#
# Takes the mac address out of the ipconfig/all output
#
def src_mac():

    lines = ipconfig_all()
    macs = []
    cnt=0
    for line in lines:
        if line != '':
            if line[0] == ' ':
                if ': ' in line:
                    key, value = line.split(': ')
                    if key.strip(' .') == 'Physical Address':
                        macs.append(value.strip())

    src_mac = macs[ constants.DEFAULT_IFACE_PLACE ].split('-')
    out_src = ''
    for part in src_mac:
        out_src += part
    return out_src

## Destination mac
# returns the mac address of the the router
#
# Takes the mac address out of the ipconfig/all output
#
def dst_mac():

    ips = []
    lines = ipconfig_all()
    for line in lines:
        if line != '':
            if line[0] == ' ':
                if ': ' in line:
                    if "Default Gateway" in line:
                        key,value = line.split(': ')
                        ips.append(value.strip())
    ip = ips[0]
    args = ["arp", "-a"]
    proc = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE)
    data = proc.stdout.read()
    rows = data.split('\r\n')
    mac = ''
    for row in rows:
        if row != '':
            if ip in row:
                mac = row[constants.START : constants.END]
    src_mac = mac.split('-')
    out_src = ''
    for part in src_mac:
        out_src += part
    return out_src
    
if __name__ == '__main__':
    main()
