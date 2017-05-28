#!/usr/bin/python

import addresses
import base64
import gcap
import ipconfigMac
import random
import re
import reply
import sys
import time



from checksum import calc_checksum

## Converts a hexstring to binary bytearray
#@ param h
def hexstring_to_binary(h, sep=''):
    return bytearray(int(x, 16) for x in re.findall('..', h.replace(sep, '')))
    
def int_to_binary(i, n):
    l = []
    for x in range(n):
        l.append(i & 0xff)
        i >>= 8
    return bytearray(l[::-1])
    
def binary_to_hexstring(h, sep=''):
    return sep.join('%02x' % x for x in bytearray(h))
    
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
def construct_packet(ip_dst,ip_src, mac_dst, mac_src,ttl,seq_num,id,cap):

    DATA_LEN = 64
    hops = []
    corr = False
    content = base64.b16encode('TRACE'+str(seq_num) )
    if len(content) < DATA_LEN:
        zeros = DATA_LEN - len(content)
        while zeros != 0:
            content += '0'
            zeros -= 1
    
    print 'SEQ: '+str(seq_num)
    packet = {
              'dst': mac_dst,
              'src': mac_src,
              'type':'0800',
              'payload':{
                   'Header Length':'45',
                   'Diff Services Field':'00',
                   'Total Length':'003c',
                   'Identification':'3db1',
                   'Fragment offset':'0000',
                   'TTL': "%02x" %ttl,
                   'Protocol':'01',
                   'Header checksum':'',
                   'src': ip_src,
                   'dst': ip_dst,
                   'payload':{
                        'Type':'08',
                        'Code':'00',
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
    
    
## Receive packet
#@ param repack(string) - reply packet
# Returns hop (string) - source ip of the packet
#
#
#
def recieve_packet(repack):

    corr = False
    exceeded = False
    timeout = False
    #target_time = time.clock() + TIME
    while not exceeded and not corr and not timeout:
        hop = reply.function(repack,cap, ip_src, mac_src, content)
        if hop != '': #if exceeded
            #hops.append(hop)
            exceeded = True
            #exceeded = reply.exceeded_reply(repack, cap, ip_src, mac_src, content)
        corr = reply.correct_reply(repack, cap, ip_src, mac_src, content)
        print '------------------------------------------------------'
    if target_time<=time.clock():
        timeout = True
    if timeout:
        print 'SEND AGAIN'
            
            
    if corr:
        print 'corr'
    return hop

def my_tracert(dest,ttl,max_time):

    ID = '0001'
    if len(sys.argv) > 1:
        iface = sys.argv[1]
    else:
        iface = gcap.GCap.get_interfaces()[0]['name']

    with gcap.GCap(iface=iface, timeout=2000) as cap:

        if '.' in dest:
            ip_dst = addresses.address_ip(dest)
        else:
            ip_dst = dest
        
        seq_num = random.randint(0,100)
        ip_src = addresses.my_ip()
        mac_dst = ipconfigMac.dst_mac()
        mac_src = ipconfigMac.src_mac()
        rand = random.randint(0,100)
        retries = 3
        status = 'NONE'
        target_time = 0
        
        """
        while True:
            repack = cap.next_packet()
            if repack:
                print 'WE HAVE A PACKET!!!!!!!!!!!!!!!!!!!!'
        """
        hop = ''
        while status == 'NONE' and retries>0:
            if target_time<=time.clock():
                seq_num += 1
                new_pack = construct_packet(ip_dst,ip_src, mac_dst, mac_src,ttl,seq_num,ID,cap)
                retries -= 1
                #sys.stderr.write(str(retries)+'\n')
                target_time = time.clock() + max_time
                print 'TIME: '+str(time.clock())

            repack = cap.next_packet()
            if repack:
                print 'WE HAVE A PACKET!!!!!!!!!!!!!!!!!!!!'
                status,hop = reply.process_packet(repack, mac_src, ip_src, seq_num,ID)
        if status == 'NONE':
            status = 'TIMOEUT'
        return status, hop


#if __name__ == '__main__':
#    main()
    
######## XML,HTTP SERVER, GIS, ETHERNET
    
    
# dst - mine
# ttl - expired / type11?

# vim: expandtab tabstop=4 shiftwidth=4