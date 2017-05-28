#!/usr/bin/python

import socket
import struct


def my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    print IP
    IP = IP.split('.')
    ip = ''
    for part in IP:
        ip += "%02x" %int(part)
    return ip
    
def mainmm():
    ifname = "eth0"
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]
    
def address_ip(hostname):
    #hostname = 'www.smartschool.co.il'
    addr = socket.gethostbyname(hostname)
    print addr
    addr = addr.split('.')
    ip = ''
    for part in addr:
        ip += "%02x" %int(part)
    return ip

def my_ip2():
    return socket.gethostbyname(socket.gethostname())
    
def main():
    'Returns a list of MACs for interfaces that have given IP, returns None if not found'
    ip='172.16.5.97'
    print ip
    for i in nif.interfaces():
        addrs = nif.ifaddresses(i)
        try:
            if_mac = addrs[nif.AF_LINK][0]['addr']
            if_ip = addrs[nif.AF_INET][0]['addr']
        except IndexError, KeyError: #ignore ifaces that dont have MAC or IP
            if_mac = if_ip = None
        if if_ip == ip:
            return if_mac
    return None


if __name__ == '__main__':
    main()