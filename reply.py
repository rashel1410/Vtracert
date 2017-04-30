#!/usr/bin/python


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
    # if len(sys.argv) > 1:
        # iface = sys.argv[1]
    # else:
        # iface = gcap.GCap.get_interfaces()[0]['name']
    
    # with gcap.GCap(iface=iface) as cap:
    
    #hops = []
    #while True:
    #packet = cap.next_packet()
    #print packet
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
    #print hops
    return ''
  
def exceeded_reply(packet, cap, my_ip, my_mac, content):
    # mac destination
    mac_dst = ('%s' % binary_to_hexstring(
        packet['data'][0:6],
    ))
    print mac_dst
    
    # ip destination
    ip_dst = ('%s' % binary_to_hexstring(
        packet['data'][30:34],
    ))
    print ip_dst
    
    # type 
    type = ('%s' % binary_to_hexstring(
        packet['data'][34:35],
    ))
    print type
    
    # icmp type 
    icmp_type = ('%s' % binary_to_hexstring(
        packet['data'][60:61],
    ))
    print icmp_type
    
    # data 
    data = ('%s' % binary_to_hexstring(
        packet['data'][68:100],
    ))
    print data
    
    print "my mac:"+my_mac
    print "mac_dst:"+mac_dst
    if (my_mac.upper() == mac_dst.upper()):
        print '>>>>>>>>>>>>>>>>>>>>>>>>'
        if (type =='0b'):
            print "my ip:"+my_ip
            print "ip dst:"+ip_dst
            if (my_ip == ip_dst):
                print 'PPPPPPPPPPPPP'
                #if data == content:
                print "*************************GOOD JOB****************************"
                return True
    return False
    
def correct_reply(packet, cap, my_ip, my_mac, content):
    # mac destination
    mac_dst = ('%s' % binary_to_hexstring(
        packet['data'][0:6],
    ))
    print mac_dst
    
    # ip source
    ip_src = ('%s' % binary_to_hexstring(
        packet['data'][26:30],
    ))
    print ip_src
    
    # ip destination
    ip_dst = ('%s' % binary_to_hexstring(
        packet['data'][30:34],
    ))
    print ip_dst
    
    # type 
    type = ('%s' % binary_to_hexstring(
        packet['data'][34:35],
    ))
    print type
    
    # # icmp type 
    # icmp_type = ('%s' % binary_to_hexstring(
        # packet['data'][60:61],
    # ))
    # print icmp_type
    
    # data 
    data = ('%s' % binary_to_hexstring(
        packet['data'][42:],
    ))
#    print data
    print "my mac 2 :"+my_mac
    print "mac_dst 2 :"+mac_dst
    if (my_mac.upper() == mac_dst.upper()):
        if (type =='00'):
            if (my_ip == ip_dst):
                #if icmp_type == '00':
                print "////////////not content//////////////"
                print data
                print ")))))))))))"
                print content
                if data == content:
                    print "reply is good"
                    print '\n'
                    return True
    print '\n'
    return False

#icmp,type,same data?
# ttl and data are changing each request


# vim: expandtab tabstop=4 shiftwidth=4
