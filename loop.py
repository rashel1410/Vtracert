#!/usr/bin/python

import my_tracert
import sys

def main():
    ttl = 1
    cur = 0 
    Hop = 'dev.gentoo.org'
    args = []
    t=5
    hop = ''
    status = 'NONE'
    while status!='REACH' and cur<20:
        status,hop = my_tracert.my_tracert(Hop,ttl,t)
        sys.stderr.write( "TTL "+str(ttl)+'\n')
        sys.stderr.write( status+'\n')
        ip = ''
        index = 0
        part = ''
        for i in range(len(hop)/2):
            part = hop[index:index+2]
            ip += str(int(part,16))+'.'
            index += 2
        ip = ip[:-1]
        sys.stderr.write(ip+'\n\n')
        ttl += 1
        cur += 1
        print 'HOPHOPHOPHOPHOPHOPHOPHOPHOPHOPHOPHOPHOPHOPHOPHOPHOPHOPHOP'
        args.append(ip)
    print args
#def my_tracert(dest,ttl,max_time):

if __name__ == '__main__':
    main()
    
#01110011-01101000-01100001-01100010-01100001-01101011
#101001 10110100 00110000 101100010 01100001 01101011