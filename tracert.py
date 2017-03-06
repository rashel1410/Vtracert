#!/usr/bin/python

import re
import sys
import gcap
import base64


def hexstring_to_binary(h, sep=''):
    return bytearray(int(x, 16) for x in re.findall('..', h.replace(sep, '')))


def int_to_binary(i, n):
    l = []
    for x in range(n):
        l.append(i & 0xff)
        i >>= 8
    return bytearray(l[::-1])


def main():
    if len(sys.argv) > 1:
        iface = sys.argv[1]
    else:
        iface = gcap.GCap.get_interfaces()[0]['name']

    with gcap.GCap(iface=iface) as cap:
        dst = 'D0:50:99:9A:AB:70'
        src = '88:1F:A1:00:CD:54'
        type = 0x1000
        send = '1056ca0b1e74881fa100cd5408004500003c3db1000080019f5fac100591ac10fffe08004d32000100296162636465666768696a6b6c6d6e6f7071727374757677616263646566676869'
        
        packet = {'dst':'1056ca0b1e74' ,
                  'src':'881fa100cd54',
                  'type':'0800',
                  'payload':{
                       'TTL':'80',
                       'Protocol':'01',
                       'Header checksum':'9f5f',
                       'src':'ac100591',
                       'dst':'ac10fffe',
                       'payload':{
                            'Type':'08',
                            'Code':'00',
                            'Checksum':'4d32'
                        }
                   }
        }
        
        # increasing TTL
        ttl = int(packet['payload']['TTL'], 16) + 1
        packet['payload']['TTL'] = hex(ttl)[-2:]
        #
        
        
        
        tosend = base64.b16decode(send,True)
        cap.send_packet(tosend
            #hexstring_to_binary(dst, sep=':') +
            #hexstring_to_binary(src, sep=':') +
            #int_to_binary(type, 2) +
            #'abcdefghijklmopqrstuvwabcdefghi'.encode('ascii')
        )


if __name__ == '__main__':
    main()


# vim: expandtab tabstop=4 shiftwidth=4
