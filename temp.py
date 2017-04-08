#!/usr/bin/python

import re
import reply
import sys
import gcap
import base64
from checksum import ip_checksum

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
    
def main():
    if len(sys.argv) > 1:
        iface = sys.argv[1]
    else:
        iface = gcap.GCap.get_interfaces()[0]['name']
    with gcap.GCap(iface=iface) as cap:
        mac_src = '881fa100cd54'
        ip_src = '0a00000a'
        content='6162636465666768696a6b6c6d6e6f7071727374757677616263646566676869'
        hops = []
        corr = False
        while not corr:
            repack = cap.next_packet()
            if repack:
                hops.append(reply.function(repack,cap, ip_src, mac_src, content))
                corr = reply.correct_reply(repack, cap, ip_src, mac_src, content)
        print hops
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