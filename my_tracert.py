#!/usr/bin/python

import addresses
import ipconfigMac
import random
import re
import reply
import sys
import gcap
import base64

from checksum import calc_checksum

TTL = 1
DATA_LEN = 64

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
    
# flag = false
# while flag==false and max<50:
# flag is true if correct reply in reply.py and max is the maximum hops number
def main():#my_tracerout(arg):

    TTL = 1
    MAX = 40
    CUR = 0
    
    if len(sys.argv) > 1:
        iface = sys.argv[1]
    else:
        iface = gcap.GCap.get_interfaces()[0]['name']

    with gcap.GCap(iface=iface) as cap:
        mac_dst = ipconfigMac.dst_mac()#'e8fcaf89a0e8' #'906cac8859af'
        mac_src = ipconfigMac.src_mac()#'881fa100cd54'
        ip_src = addresses.my_ip()#'0a000008' #'ac1001e0'
        type_ = 0x1000
        hops = []
        corr = False
        #if ip address
        # ip_dst_list = arg.split('.')
        # ip_dst= ''
        # print arg
       # # print arg.encode('utf8')
        # print ip_dst_list
        # for part in ip_dst_list:
            # ip_dst += '%02x' %int(part.encode())
        # print ip_dst
        arg = '8.8.8.8'
        ip_dst = addresses.address_ip(arg)#'08080808'
        
        print mac_dst
        print mac_src
        print ip_dst
        print ip_src
        
        ### what if arg is www.ynet.co.il and not ip ????????? what if packets don't come each after other but : request request reply reply

        while not corr and CUR<MAX:
            rand = random.randint(0,100)
            content = base64.b16encode('TRACE'+str(rand) ) # '6162636465666768696a6b6c6d6e6f7071727374757677616263646566676869'
            if len(content) < DATA_LEN:
                zeros = DATA_LEN - len(content)
                while zeros != 0:
                    content += '0'
                    zeros -= 1
                    
            packet = {
                      'dst': mac_dst, # 
                      'src': mac_src, #'881fa100cd54',
                      'type':'0800',
                      'payload':{
                           'Header Length':'45',
                           'Diff Services Field':'00',
                           'Total Length':'003c',
                           'Identification':'3db1',
                           'Fragment offset':'0000',
                           'TTL': "%02x" %TTL,
                           'Protocol':'01',
                           'Header checksum':'',
                           'src': ip_src,#'0a000008', #'ac1001e0',
                           'dst': ip_dst,
                           'payload':{
                                'Type':'08',
                                'Code':'00',
                                'Checksum':'',
                                'Identifier':'0001',
                                'Sequence num':'%04x' %rand,
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
            #print 'new chsum'
            hex_ip_chsum = "%04x" %ip_chsum
            packet['payload']['Header checksum'] = hex_ip_chsum
            #print packet['payload']['Header checksum']
            
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
            hex_data_chsum = "%02x" %data_chsum
            packet['payload']['payload']['Checksum'] = hex_data_chsum
            #print packet['payload']['payload']['Checksum']
            
            
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
            TTL += 1

            # increasing TTL
            #ttl = int(packet['payload']['TTL'], 16) + 1
            #packet['payload']['TTL'] = hex(ttl)[-2:]
            #
            
            
    #        hops = []
            #print new_pack
            tosend = base64.b16decode(new_pack,True)
            cap.send_packet(tosend)
    #        corr = False
    #        while not corr:
            repack = cap.next_packet()
            if repack:
                hop = reply.function(repack,cap, ip_src, mac_src, content)
                if hop != '': #if exceeded
                    hops.append(hop)
                corr = reply.correct_reply(repack, cap, ip_src, mac_src, content)
                    #print repack
            CUR += 1
        hops.append(ip_dst)
        print hops
        
        new_hops = []
        for h in hops:
            dec_hop = ''
            last = ''
            index = 0
            for i in range(len(h)/2):
                print h[index:index+2]
                dec_hop += str(int((h[index:index+2]), 16)) 
                dec_hop += '.'
                index += 2
            dec_hop = dec_hop[:-1]
            if new_hops != last:
                new_hops.append(dec_hop)
                last = dec_hop
        print new_hops
        return new_hops
#   CHECK WHY CHANGING THE DATA CAUSING PROBLEMS - EXCEEDED IS FINE BUT DOESNT GETTING A REPLY
#   SEND NEW_HOPS TO SERVER OR JAVASCRIPT AND USE IN MAP
#   WHY CONSTANS DON'T WORK WELL
        
        
        
            #hexstring_to_binary(dst, sep=':') +
            #hexstring_to_binary(src, sep=':') +
            #int_to_binary(type, 2) +
            #'abcdefghijklmopqrstuvwabcdefghi'.encode('ascii')
        
#906cac8859af881fa100cd5408004500004d24434000800673aeac1006a9ae81017fe0421acdd873
#fe37decea8455018010163fb0000ca1c2cb079f5ada942b5bdc5911886eec5e2bb80e5a5b8fec28b
#aa6f407447aeedfef20d63

if __name__ == '__main__':
    main()
    
# dst - mine
# ttl - expired / type11?

# vim: expandtab tabstop=4 shiftwidth=4