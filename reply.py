#!/usr/bin/python
""" works with icmp reply packets """
## @file reply.py Functions that are used for reply packets

import addresses
import gcap
import ipconfigMac
import sys


## Converts binary to hexstring
#@ param h (bin)
#@ param sep (string)
# returns hexstring
#
def binary_to_hexstring(h, sep=''):
    return sep.join('%02x' % x for x in bytearray(h))

## If correct addresses
#@ param packet (string)
#@ param my_ip (string)
#@ param my_mac (string)
#
# The function checks all the addresses and returns true
# if the packet is exceeded_reply or echo reply
#
def correct_addresses(packet, my_ip, my_mac):
    
    TTL_EXCEEDED = '0b'
    ECHO_REPLY = '00'
    ETH_TYPE = '0800'
    ICMP = '01'
    # mac destination
    mac_dst = ('%s' % binary_to_hexstring(
        packet['data'][0:6],
    ))
    #print 'Mac_dst: '+mac_dst
    # Ethernet type 
        
    eth_type = ('%s' % binary_to_hexstring(
        packet['data'][12:14],
    ))
    #print 'eth_type: '+eth_type
    
    # ip protocol 
    ip_protocol = ('%s' % binary_to_hexstring(
        packet['data'][23:24],
    ))
    #print 'ip protocol: '+ip_protocol
    
    # ip destination
    ip_dst = ('%s' % binary_to_hexstring(
        packet['data'][30:34],
    ))
    
    # icmp type 
    icmp_type = ('%s' % binary_to_hexstring(
        packet['data'][34:35],
    ))

    # data 
    data = ('%s' % binary_to_hexstring(
        packet['data'][68:100],
    ))
    #print data
    if icmp_type != '08':
        print "REPLY"
    
    print "my mac:"+my_mac
    print "mac_dst:"+mac_dst
    if (my_mac.upper() == mac_dst.upper())and(eth_type == ETH_TYPE):
    
        """print 'Mac_dst: '+mac_dst
        print 'eth_type: '+eth_type
        print 'ip protocol: '+ip_protocol
        print 'ip_dst: '+ip_dst
        print 'icmp_type: '+icmp_type
        print 'my_ip == ip_dst: '
        print my_ip == ip_dst and ip_protocol==ICMP
        print 'MY IP: '+'.'+my_ip+'.'
        print 'ID DST: '+'.'+ip_dst+'.'"""
        
        if (my_ip == ip_dst)and(ip_protocol==ICMP):
            if icmp_type in (TTL_EXCEEDED, ECHO_REPLY):
                return True
    return False
    
    
## True if exceeded reply
#@ param packet (string)
#@ param my_ip (string)
#@ param my_mac (string)
#
# The function returns true if the packet is exceeded - type '0b' (11)
#
def exceeded_reply(packet, my_ip, my_mac):

    # type 
    type = ('%s' % binary_to_hexstring(
        packet['data'][34:35],
    ))
    print type

    for_me = correct_addresses(packet, my_ip, my_mac)
    if for_me:
        if type == '0b':
            return True
    return False
    
## True if exceeded reply
#@ param packet (string)
#@ param my_ip (string)
#@ param my_mac (string)
# returns true/false
#
# The function returns true if the packet is echo reply - type '00'
#
def correct_reply(packet, my_ip, my_mac):#, content):

    # type 
    type = ('%s' % binary_to_hexstring(
        packet['data'][34:35],
    ))
    print type

    for_me = correct_addresses(packet, my_ip, my_mac)
    if for_me:
        if type == '00':
            return True
    return False

## True if exceeded reply
#@ param packet (string)
#@ param my_ip (string)
#@ param my_mac (string)
#@ req_seq_num (int) - sequence number that increases in each echo request we send
#@ ID (string) - constant field
# returns hop (string-address) and status(string-HOP/REACH/NONE)
#
# if exceeded reply - HOP - ip address
# if echo reply - REACH - ip address
# if none of the above - NONE - ip address = ''
#
def process_packet(packet, my_mac, my_ip, req_seq_num,ID):

    hop = ''
    status = 'NONE'
    if packet:
        if correct_reply(packet,my_ip,my_mac):
            identifier = ('%s' % binary_to_hexstring(
                packet['data'][38:40],
            ))
            print 'identifier: '+identifier

            seq = ('%s' % binary_to_hexstring(
                packet['data'][40:42],
            ))
            print 'seq: '+seq
            print 'Req_seq: '+'%04x' %req_seq_num
            
            if identifier == ID and seq == '%04x' %req_seq_num:
                status = 'REACH'
                hop = ('%s' % binary_to_hexstring(
                    packet['data'][26:30],
                ))
            
            
        elif exceeded_reply(packet,my_ip,my_mac):
            identifier = ('%s' % binary_to_hexstring(
                packet['data'][66:68],
            ))
            print 'identifier: '+identifier

            seq = ('%s' % binary_to_hexstring(
                packet['data'][68:70],
            ))
            print 'seq: '+seq
            print 'Req_seq: '+'%04x' %req_seq_num
            
            if identifier == ID and seq == '%04x' %req_seq_num:
                status = 'HOP'
                hop = ('%s' % binary_to_hexstring(
                    packet['data'][26:30],
                ))
    print status,hop
    return status,hop


# vim: expandtab tabstop=4 shiftwidth=4
