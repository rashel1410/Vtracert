#!/usr/bin/python

import addresses
import ipconfigMac
import sys
import gcap
#import gcap.winpcapy


def binary_to_int(h):
    ret = 0
    for x in bytearray(h):
        ret = (ret << 8) + x
    return ret


def binary_to_hexstring(h, sep=''):
    return sep.join('%02x' % x for x in bytearray(h))


def function(packet, cap, my_ip, my_mac, content):

    if packet:
        # ip source
        ip_src = ('%s' % binary_to_hexstring(
            packet['data'][26:30],
        ))
        #print ip_src
        if exceeded_reply(packet, cap,my_ip,my_mac, content):
            #hops.append(ip_src)
            return ip_src
        elif correct_reply(packet, cap,my_ip,my_mac, content):
            print "correct R"
    return ''

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
    #print 'ip_dst: '+ip_dst
    
    # icmp type 
    icmp_type = ('%s' % binary_to_hexstring(
        packet['data'][34:35],
    ))
    #print 'icmp_type: '+icmp_type
    
    # icmp protocol 
    # icmp_protocol = ('%s' % binary_to_hexstring(
        # packet['data'][51:52],
    # ))
    # print 'icmp protocol: '+icmp_protocol
    
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
        #print '>>>>>>>>>>>>>>>>>>>>>>>>'
        print 'Mac_dst: '+mac_dst
        print 'eth_type: '+eth_type
        print 'ip protocol: '+ip_protocol
        print 'ip_dst: '+ip_dst
        print 'icmp_type: '+icmp_type
        print 'my_ip == ip_dst: '
        print my_ip == ip_dst and ip_protocol==ICMP
        print 'MY IP: '+'.'+my_ip+'.'
        print 'ID DST: '+'.'+ip_dst+'.'
        if (my_ip == ip_dst)and(ip_protocol==ICMP):
            #print '>>>>>>>>>>>>>>>>>>>>>>>>'
            if icmp_type in (TTL_EXCEEDED, ECHO_REPLY):
                #print '>>>>>>>>>>>>>>>>>>>>>>>>'
                
                return True
    #print '++++++++++++++++++++++++++++++++++++++++++++++++++'
    return False
    
    
def exceeded_reply(packet, my_ip, my_mac):#, content):

    # type 
    type = ('%s' % binary_to_hexstring(
        packet['data'][34:35],
    ))
    print type

    for_me = correct_addresses(packet, my_ip, my_mac)
    if for_me:
        print '<<<<<<<<<<<<<<<<<<<'
        if type == '0b':
            return True
    return False
    
def correct_reply(packet, my_ip, my_mac):#, content):

    # type 
    type = ('%s' % binary_to_hexstring(
        packet['data'][34:35],
    ))
    print type

    for_me = correct_addresses(packet, my_ip, my_mac)
    if for_me:
        print '????????????????????????????????????'
        if type == '00':
            return True
    return False

def process_packet(packet, my_mac, my_ip, req_seq_num,ID):#content???

    hop = ''
    status = 'NONE'
    #print 'EXCEEEEEEEDEEDDDDDDDDDDDDD@@@@@@@@@@@@@@@@@@@@@@@@@@@'
    if packet:
        #print 'EXCEEEEEEEDEEDDDDDDDDDDDDD@@@@@@@@@@@@@@@@@@@@@@@@@@@'
        if correct_reply(packet,my_ip,my_mac):#, content):
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
            
            
        elif exceeded_reply(packet,my_ip,my_mac):#, content):
            #print 'EXCEEEEEEEDEEDDDDDDDDDDDDD@@@@@@@@@@@@@@@@@@@@@@@@@@@'
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
    #sys.stderr.write( "TTL "+str(ttl)+'\n')
    #sys.stderr.write( status+'\n')
    #sys.stderr.write(hop+'\n')
    print status,hop
    return status,hop
    
    
#icmp,type,same data?
# ttl and data are changing each request


# vim: expandtab tabstop=4 shiftwidth=4
