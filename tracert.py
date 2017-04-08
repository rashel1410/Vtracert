#!/usr/bin/python

import re
import reply
import sys
import gcap
import base64

from checksum import ip_checksum

TTL = 1

def hexstring_to_binary(h, sep=''):
    return bytearray(int(x, 16) for x in re.findall('..', h.replace(sep, '')))
    
def int_to_binary(i, n):
    l = []
    for x in range(n):
        l.append(i & 0xff)
        i >>= 8
    return bytearray(l[::-1])

def to_bin(str):
    binS = bin(int(str,16))
    num = 0
    
def binary_to_hexstring(h, sep=''):
    return sep.join('%02x' % x for x in bytearray(h))
    
# flag = false
# while flag==false and max<50:
# flaf is true if correct reply in reply.py and max is the maximum hops number
def main():
    TTL = 1
    MAX = 50
    CUR = 0
    
    if len(sys.argv) > 1:
        iface = sys.argv[1]
    else:
        iface = gcap.GCap.get_interfaces()[0]['name']
    #print iface
    with gcap.GCap(iface=iface) as cap:
        mac_dst = 'e8fcaf89a0e8' #'906cac8859af'
        mac_src = '881fa100cd54'
        ip_src = '0a00000a' #'ac1001e0'
        type = 0x1000
        #send = '1056ca0b1e74881fa100cd5408004500003c3db1000002019f5fac100591ac10fffe08004d32000100296162636465666768696a6b6c6d6e6f7071727374757677616263646566676869'
        content = '6162636465666768696a6b6c6d6e6f7071727374757677616263646566676869' #base64.b16encode('RASHEL 1') # '6162636465666768696a6b6c6d6e6f7071727374757677616263646566676869'
#        content += '000000000000000000000000000000000000000000000000'
        
        hops = []
        corr = False
        while not corr and CUR<MAX:
            packet = {
                      'dst': 'e8fcaf89a0e8', #'906cac8859af' ,
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
                           'src': '0a00000a', #'ac1001e0',
                           'dst':'08080808',
                           'payload':{
                                'Type':'08',
                                'Code':'00',
                                'Checksum':'4d32',
                                'Identifier':'0001',
                                'Sequence num':'0029',
                                'Data': content
                            }
                       }
            }
            
            Z = [
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
            for p in Z:
                out += p
            print out
            List=[]
            index=0
            for l in range(len(out)/2):
                List.append(hexstring_to_binary(out[2*l] + out[(2*l)+1]))
                index += 2
            #print List
            
           # for g in Y:
            #    print g
                
            
            chsum = ip_checksum(List, len(List))
            print 'new chsum'
            hex_chsum = "%04x" %chsum
            #print chsum
            packet['payload']['Header checksum'] = hex_chsum
            print packet['payload']['Header checksum']
            # building the packet
            X = [
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
            for item in X:
                new_pack += item
            TTL += 1
            #replyPack = cap.next_packet()
            #print binary_to_hexstring(replyPack['data'])
            #print replyPack
            
                
                
            # increasing TTL
            #ttl = int(packet['payload']['TTL'], 16) + 1
            #packet['payload']['TTL'] = hex(ttl)[-2:]
            #
            
            
    #        hops = []
            tosend = base64.b16decode(new_pack,True)
            cap.send_packet(tosend)
    #        corr = False
    #        while not corr:
            repack = cap.next_packet()
            if repack:
                hop = reply.function(repack,cap, ip_src, mac_src, content)
                if hop != '':
                    hops.append(hop)
                    corr = reply.correct_reply(repack, cap, ip_src, mac_src, content)
                    #print repack
            CUR += 1
        print hops
        
        new_hops = []
        for h in hops:
            dec_hop = ''
            index = 0
            for i in range(len(h)/2):
                print h[index:index+2]
                dec_hop += str(int((h[index:index+2]), 16)) 
                dec_hop += '.'
                index += 2
            new_hops.append(dec_hop)
        print new_hops
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