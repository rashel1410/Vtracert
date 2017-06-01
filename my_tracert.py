#!/usr/bin/python
""" my tracert """
## @file my_tracert.py Traces to a given destination
import addresses
import base64
import gcap
import ipconfigMac
import random
import re
import reply
import sys
import time
import datetime

from common import constants
from checksum import calc_checksum

## Converts a hexstring to binary bytearray
#@ param h (string)
#@ param sep (string)
# returns a bytearray
#
def hexstring_to_binary(h, sep=''):
    return bytearray(int(x, 16) for x in re.findall('..', h.replace(sep, '')))
    

## Converts a string to binary list
#@ param s (string)
# returns a bytearray
#
def binary_list(s):
    out = []
    index = 0
    for l in range(len(s)/2):
        out.append(hexstring_to_binary( s[2*l] + s[(2*l)+1]))
        index += 2
    return out


## Construct packet
#@ param ip_dst (string)
#@ param ip_src (string)
#@ param mac_dst (string)
#@ param mac_src (string)
#@ param ttl (int) - time to live
#@ param seq_num (int) - initially a random number that increases with every new packet
#@ param id (int) - identification number
#@ param cap (gcap) - gcap object
# returns a (string) packet
#
# The function constructs an icmp request packet
# that contains the arguments it got
#
def construct_packet(ip_dst,ip_src, mac_dst, mac_src,ttl,seq_num,id,cap,fd,to_file):

    hops = []
    content = base64.b16encode('TRACE'+str(seq_num) )
    if len(content) < constants.DATA_LEN:
        zeros = constants.DATA_LEN - len(content)
        while zeros != 0:
            content += '0'
            zeros -= 1
    if to_file:
        fd.write( 'SEQ: '+str(seq_num) )
        fd.write( ip_dst )
    
    packet = {
              'dst': mac_dst,
              'src': mac_src,
              'type': constants.ETH_TYPE,
              'payload':{
                   'Header Length': constants.HEADER_LEN,
                   'Diff Services Field': constants.DIFF_FIELD,
                   'Total Length': constants.TOTAL_LEN,
                   'Identification': constants.IDENTIFICATION,
                   'Fragment offset': constants.FRAGM_OFFSET,
                   'TTL': "%02x" %ttl,
                   'Protocol': constants.IP_PROT,
                   'Header checksum':'',
                   'src': ip_src,
                   'dst': ip_dst,
                   'payload':{
                        'Type': constants.ICMP_ECHO_TYPE,
                        'Code': constants.ICMP_CODE,
                        'Checksum':'',
                        'Identifier':id,
                        'Sequence num':'%04x' %seq_num,
                        'Data': content
                    }
               }
    }
    
    ip_headers = [
        packet['payload']['Header Length'],
        packet['payload']['Diff Services Field'],
        packet['payload']['Total Length'],
        packet['payload']['Identification'],
        packet['payload']['Fragment offset'],
        packet['payload']['TTL'],
        packet['payload']['Protocol'],
        packet['payload']['src'],
        packet['payload']['dst']
    ]
    
    out=''
    for p in ip_headers:
        out += p
    bin_list = binary_list(out)
    
    # ip checksum calculation
    ip_chsum = calc_checksum(bin_list, len(bin_list))
    hex_ip_chsum = "%04x" %ip_chsum
    packet['payload']['Header checksum'] = hex_ip_chsum
    
    data_headers = [
        packet['payload']['payload']['Type'],
        packet['payload']['payload']['Code'],
        packet['payload']['payload']['Identifier'],
        packet['payload']['payload']['Sequence num'],
        packet['payload']['payload']['Data']
    ]
    
    out=''
    for p in data_headers:
        out += p
    bin_list = binary_list(out)
    
    # data checksum calculation
    data_chsum = calc_checksum(bin_list, len(bin_list))
    hex_data_chsum = "%04x" %data_chsum
    packet['payload']['payload']['Checksum'] = hex_data_chsum
    
    
    # building the packet
    done_pack = [
        packet['dst'],
        packet['src'],
        packet['type'],
        packet['payload']['Header Length'],
        packet['payload']['Diff Services Field'],
        packet['payload']['Total Length'],
        packet['payload']['Identification'],
        packet['payload']['Fragment offset'],
        packet['payload']['TTL'],
        packet['payload']['Protocol'],
        packet['payload']['Header checksum'],
        packet['payload']['src'],
        packet['payload']['dst'],
        packet['payload']['payload']['Type'],
        packet['payload']['payload']['Code'],
        packet['payload']['payload']['Checksum'],
        packet['payload']['payload']['Identifier'],
        packet['payload']['payload']['Sequence num'],
        packet['payload']['payload']['Data']
    ]

    new_pack = ''
    for item in done_pack:
        new_pack += item
    send_my_packet(new_pack,cap)
    
    if to_file:
        fd.write( new_pack )
    return new_pack
    
    
## Send request packet
#@ param new_pack (string) - icmp request packet to send
#@ param cap (gcap) - gcap object
#
# Sends the packet using gcap
#
def send_my_packet(new_pack,cap):
    tosend = base64.b16decode(new_pack,True)
    cap.send_packet(tosend)
    
    
## My Tracert
#@ param dest (string) - destination ip or dns address
#@ param ttl (int) - time to live value
#@ param max_time (int) - seconds till timeout
# returns hop (string-address) and status(string-HOP/REACH/TIMEOUT)
#
# Sends an icmp echo request packet to the given destination
# trys 3 times, if no related reply - echo reply/exceeded reply sends status TIMEOUT
# else - when recognizes echo reply packet - REACH/ exceeded reply - HOP
#
def my_tracert(dest,ttl,max_time,mac,to_file):
    
    iface = gcap.GCap.get_interfaces()[0]['name']
    with gcap.GCap( iface = iface, timeout = 2000 ) as cap:
        with open('debug_output.txt', 'w') as fd:

            if '.' in dest:
                ip_dst = addresses.address_ip(dest)
            else:
                ip_dst = dest
            
            seq_num = random.randint(0,100)
            ip_src = addresses.my_ip()
            mac_dst = ipconfigMac.dst_mac()
            if mac == 'GET_MAC':
                mac_src = ipconfigMac.src_mac()
            else:
                mac_src = mac
            if to_file:
                fd.write( mac_src )
                
            rand = random.randint(0,100)
            retries = 3
            status = 'NONE'
            target_time = 0
            time_before = datetime.datetime.now()
            
            """
            while True:
                repack = cap.next_packet()
                if repack:
                    fd.write( 'WE HAVE A PACKET!!!!!!!!!!!!!!!!!!!!'
            """
            hop = ''
            while status == 'NONE' and retries>0:
                if target_time<=time.clock():
                    seq_num += 1
                    new_pack = construct_packet(ip_dst,ip_src, mac_dst, mac_src,ttl,seq_num,constants.ID,cap,fd,to_file)
                    retries -= 1
                    target_time = time.clock() + max_time
                    if to_file:
                        fd.write( 'TIME: '+str(time.clock()) )

                repack = cap.next_packet()
                if repack:
                    if to_file:
                        fd.write( 'WE HAVE A PACKET!!!!!!!!!!!!!!!!!!!!' )
                    status,hop = reply.process_packet(repack, mac_src, ip_src, seq_num,constants.ID,fd, to_file)
                    
            time_after = datetime.datetime.now()
            delta = time_after - time_before
            cur_delta =  (delta.total_seconds() * 1000) + (delta.microseconds / 1000)

            if status == 'NONE':
                status = 'TIMEOUT'
            return status, hop, cur_delta

# vim: expandtab tabstop=4 shiftwidth=4