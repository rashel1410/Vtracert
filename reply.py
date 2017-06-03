#!/usr/bin/python
""" works with icmp reply packets """
## @file reply.py Functions that are used for reply packets

import addresses
import gcap
import ipconfigMac

from common import constants

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
#@ param fd (int) - file descriptor to write to
#@ param to_file (boolean) - true if user asked to write into debug file
# The function checks all the addresses and returns true
# if the packet is exceeded_reply or echo reply
#
def correct_addresses(packet, my_ip, my_mac, fd, to_file):
    
    # mac destination
    mac_dst = ('%s' % binary_to_hexstring(
        packet['data'][0:6],
    ))

    # Ethernet type 
        
    eth_type = ('%s' % binary_to_hexstring(
        packet['data'][12:14],
    ))
    
    # ip protocol 
    ip_protocol = ('%s' % binary_to_hexstring(
        packet['data'][23:24],
    ))
    
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

    if icmp_type != '08':
        if to_file:
            fd.write( "REPLY" )
        
    if to_file:
        fd.write( "my mac:"+my_mac )
        fd.write( "mac_dst:"+mac_dst )
        
    if (my_mac.upper() == mac_dst.upper())and(eth_type == constants.ETH_TYPE):
        if to_file:
            fd.write( 'Mac_dst: '+mac_dst)
            fd.write( 'eth_type: '+eth_type)
            fd.write( 'ip protocol: '+ip_protocol)
            fd.write( 'ip_dst: '+ip_dst)
            fd.write( 'icmp_type: '+icmp_type)
            fd.write( 'my_ip == ip_dst: ')
            fd.write( 'MY IP: '+'.'+my_ip+'.')
            fd.write( 'id DST: '+'.'+ip_dst+'.' )
        
        if (my_ip == ip_dst)and(ip_protocol == constants.ICMP):
            if icmp_type in (constants.TTL_EXCEEDED, constants.ECHO_REPLY):
                return True
    return False
    
    
## True if exceeded reply
#@ param packet (string)
#@ param my_ip (string)
#@ param my_mac (string)
#@ param fd (int) - file descriptor to write to
#@ param to_file (boolean) - true if user asked to write into debug file#
# The function returns true if the packet is exceeded - type '0b' (11)
#
def exceeded_reply(packet, my_ip, my_mac, fd, to_file):

    # type 
    type = ('%s' % binary_to_hexstring(
        packet['data'][34:35],
    ))
    if to_file:
        fd.write( type )

    for_me = correct_addresses(packet, my_ip, my_mac, fd, to_file)
    if for_me:
        if type == constants.TTL_EXCEEDED:
            return True
    return False
    
## True if exceeded reply
#@ param packet (string)
#@ param my_ip (string)
#@ param my_mac (string)
#@ param fd (int) - file descriptor to write to
#@ param to_file (boolean) - true if user asked to write into debug file
# returns true/false
#
# The function returns true if the packet is echo reply - type '00'
#
def correct_reply(packet, my_ip, my_mac, fd, to_file):

    # type 
    type = ('%s' % binary_to_hexstring(
        packet['data'][34:35],
    ))
    if to_file:
        fd.write( type )

    for_me = correct_addresses(packet, my_ip, my_mac, fd, to_file)
    if for_me:
        if type == constants.ECHO_REPLY:
            return True
    return False

## True if exceeded reply
#@ param packet (string)
#@ param my_ip (string)
#@ param my_mac (string)
#@ req_seq_num (int) - sequence number that increases in each echo request we send
#@ id (string) - constant field
#@ param fd (int) - file descriptor to write to
#@ param to_file (boolean) - true if user asked to write into debug file
# returns hop (string-address) and status(string-HOP/REACH/NONE)
#
# if exceeded reply - HOP - ip address
# if echo reply - REACH - ip address
# if none of the above - NONE - ip address = ''
#
def process_packet(packet, my_mac, my_ip, req_seq_num, id, fd, to_file):

    hop = ''
    status = 'NONE'
    if packet:
        if correct_reply(packet,my_ip,my_mac, fd, to_file):
            identifier = ('%s' % binary_to_hexstring(
                packet['data'][38:40],
            ))
            if to_file:
                fd.write( 'identifier: '+identifier )

            seq = ('%s' % binary_to_hexstring(
                packet['data'][40:42],
            ))
            if to_file:
                fd.write( 'seq: '+seq )
                fd.write( 'Req_seq: '+'%04x' %req_seq_num )
            
            if identifier == id and seq == '%04x' %req_seq_num:
                status = 'REACH'
                hop = ('%s' % binary_to_hexstring(
                    packet['data'][26:30],
                ))
            
            
        elif exceeded_reply(packet,my_ip,my_mac, fd, to_file):
            identifier = ('%s' % binary_to_hexstring(
                packet['data'][66:68],
            ))
            if to_file:
                fd.write( 'identifier: '+identifier )

            seq = ('%s' % binary_to_hexstring(
                packet['data'][68:70],
            ))
            if to_file:
                fd.write( 'seq: '+seq )
                fd.write( 'Req_seq: '+'%04x' %req_seq_num )
            
            if identifier == id and seq == '%04x' %req_seq_num:
                status = 'HOP'
                hop = ('%s' % binary_to_hexstring(
                    packet['data'][26:30],
                ))
    if to_file:
        fd.write( status )
        fd.write( hop )
    return status,hop


# vim: expandtab tabstop=4 shiftwidth=4
