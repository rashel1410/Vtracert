#!/usr/bin/env python
""" checksum """
## @file checksum.py Written by Grant Curell
#-------------------------------------------------------------------------------
# Name:        checksum.py
#
# Author:      Grant Curell
#
# Created:     16 Sept 2012
#
# Description: Calculates the checksum for an IP header
#-------------------------------------------------------------------------------
    
    
## Calculate the checksum
#@ param header (string) - headers of the packet
#@ param size (int) - header size - to check if odd
#
def calc_checksum(header, size):
    
    cksum = 0
    pointer = 0
    
    while size > 1:
        cksum += int(((header[pointer][0]) << 8)+(header[pointer+1][0]))
        
        #cksum += int((str("%02x" % (ip_header[pointer],)) + 
        #              str("%02x" % (ip_header[pointer+1],))), 16)
        # print cksum
        # print size
        size -= 2
        pointer += 2
    if size: #This accounts for a situation where the header is odd
        cksum += header[pointer][0]
    cksum = (cksum >> 16) + (cksum & 0xffff)
    cksum += (cksum >>16)
    
    return (~cksum) & 0xFFFF