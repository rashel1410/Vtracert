#!/usr/bin/python

import argparse
import contextlib
import datetime
import errno
import os
import socket
import subprocess
import sys
import traceback
import urlparse
import xml
import xml.etree.ElementTree as et

from common import constants
from common import util
from my_tracert import my_tracert
TTL = 1
MAX_HOPS = 30
RETRIES = 3
IP_BEG = 32
CUR_HOPS = 0
MIME_MAPPING = {
    'xml': 'text/xml',
    'html': 'text/html',
    'png': 'image/png',
    'txt': 'text/plain',
}


# parsing
def parse_args():
    """Parse program argument."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--bind-address',
        default='0.0.0.0',
        help='Bind address, default: %(default)s',
    )
    parser.add_argument(
        '--bind-port',
        default=constants.DEFAULT_HTTP_PORT,
        type=int,
        help='Bind port, default: %(default)s',
    )
    parser.add_argument(
        '--base',
        default='.',
        help='Base directory to search fils in, default: %(default)s',
    )
    args = parser.parse_args()
    args.base = os.path.normpath(os.path.realpath(args.base))
    return args


# used for errors
def send_status(s, code, message, extra):

    util.send_all(
        s,
        (
            (
                '%s %s %s\r\n'
                'Content-Type: text/plain\r\n'
                '\r\n'
                'Error %s %s\r\n'
                '%s'
            ) % (
                constants.HTTP_SIGNATURE,
                code,
                message,
                code,
                message,
                extra,
            )
        ).encode('utf-8')
    )


# gets an address, tracerouts, returns list of ips
def tracerout_to_ip(address):

    args = ["tracert", "-d", address]
    proc = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE)
    print 'tracing'
    data = proc.communicate()[0]
    lines = data.split('\r\n')
    ip_list = []
    for line in lines:
        if line != "":
            if line[0] == ' ':
                ip = line[IP_BEG:]
                ip = ip.strip(' ')
                if ip != 'Request timed out.':
                    ip_list.append(ip)
            else:
                print line
    print 6666666666666666666666
    print type(ip_list[0])
    print ip_list
    return ip_list


# gets list - creates and returns an xml
def create_xml(ip):

    root = et.Element('list')
    title = et.SubElement(root, 'ipAddr')
    title.text = ip
    print ip
    print et.tostring(root)
    return et.tostring(root)


def main():

    args = parse_args()
    print 'start...'
    with contextlib.closing(
        socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        )
    ) as sl:
        sl.bind((args.bind_address, args.bind_port))
        sl.listen(10)
        while True:
            s, addr = sl.accept()
            with contextlib.closing(s):
                status_sent = False
                try:
                    rest = bytearray()
                    #
                    # Parse request line
                    #
                    req, rest = util.recv_line(s, rest)
                    req_comps = req.split(' ', 2)

                    if len(req_comps) == 1:
                        req_comps = req

                    else:
                        if req_comps[2] != constants.HTTP_SIGNATURE:
                            raise RuntimeError('Not HTTP protocol')
                        if len(req_comps) != 3:
                            raise RuntimeError('Incomplete HTTP protocol')
                        print(req_comps)

                        method, uri, signature = req_comps
                        if method != 'GET':
                            raise RuntimeError(
                                "HTTP unsupported method '%s'" % method
                            )
                    #
                    # Create a file out of request uri.
                    # Be extra careful, it must not escape
                    # the base path.
                    #
                    # NOTICE: os.path.normpath cannot be used checkout:
                    # os.path.normpath(('/a/b', '/a/b1')
                    #
                    if not uri or uri[0] != '/':
                        raise RuntimeError("Invalid URI")
                    file_name = os.path.normpath(
                        os.path.join(
                            args.base,
                            uri[1:],
                        )
                    )

                    if uri[:11] == '/ip_or_dns?':
                        #status,hop = my_tracerout(ip_or_dns)
                        
                        parse = urlparse.urlparse(uri)
                        ip_or_dns = parse.query
                        MAX_TIME = 5
                        TTL = 1
                        MAX_HOPS = 30
                        RETRIES = 3
                        IP_BEG = 32
                        CUR_HOPS = 0
                        hop = ''
                        status = 'NONE'
                        ok = True
                        while status!='REACH' and CUR_HOPS < MAX_HOPS:
                            if ok:
                                util.send_all(
                                    s,
                                    (
                                            (
                                                '%s 200 OK\r\n'
                                            ) % (
                                                constants.HTTP_SIGNATURE,
                                            )
                                    ).encode('utf-8')
                                )
                                status,hop = my_tracert(ip_or_dns,TTL,MAX_TIME)
                                sys.stderr.write( "TTL "+str(TTL)+'\n')
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
                                TTL += 1
                                CUR_HOPS += 1
                                print 'HOPHOPHOPHOPHOPHOPHOPHOPHOPHOPHOPHOPHOPHOPHOPHOPHOPHOPHOP'
                                #print type(ip_or_dns)
                                #tracerout_to_ip(ip_or_dns)
                                out = create_xml(ip)
                                #print out
                                util.send_all(
                                    s,
                                    (
                                            (
                                                'Content-Length: %s\r\n'
                                                'Content-Type: %s\r\n'
                                                '\r\n'
                                            ) % (
                                                len(out),
                                                MIME_MAPPING.get('xml'),
                                            )
                                    ).encode('utf-8')
                                )
                                util.send_all(s, out)
                            print uri[:9]
                            if uri[:9] != '/next hop':
                                ok = False
                            else:
                                ok = True

                    # elif uri[:6] == '/list?':
                        # parse = urlparse.urlparse(uri)
                        # ip_list = parse.query
                        # print ip_list
                        # util.send_all(
                            # (
                                # s,
                                # (
                                    # '%s 200 OK\r\n'
                                    # 'Content-Length: %s\r\n'
                                    # 'Content-Type: %s\r\n'
                                    # '\r\n'
                                # ) % (
                                        # constants.HTTP_SIGNATURE,
                                        # len(out),
                                        # MIME_MAPPING.get('http'),
                                    # )
                                # ).encode('utf-8')
                            # )
                        # util.send_all(s, out)
                    else:
                        with open(file_name, 'rb') as f:
                            util.send_all(
                                s,
                                (
                                    (
                                        '%s 200 OK\r\n'
                                        'Content-Length: %s\r\n'
                                        'Content-Type: %s\r\n'
                                        '\r\n'
                                    ) % (
                                        #
                                        # 'HTTP/1.1'
                                        # size of file
                                        # file type (.py , .html .....)=>
                                        # => goes to MIME_MAPPING.
                                        #
                                        constants.HTTP_SIGNATURE,
                                        os.fstat(f.fileno()).st_size,
                                        MIME_MAPPING.get(
                                            os.path.splitext(
                                                file_name
                                            )[1].lstrip('.'),
                                            MIME_MAPPING.get('http'),
                                        )
                                    )
                                ).encode('utf-8')
                            )
                            # reading file
                            while True:
                                buff = f.read(constants.BLOCK_SIZE)
                                if not buff:
                                    break
                                util.send_all(s, buff)
                        #
                        # Send content
                        #
                except IOError as e:
                    traceback.print_exc()
                    if not status_sent:
                        if e.errno == errno.ENOENT:
                            send_status(s, 404, 'File Not Found', e)
                        else:
                            send_status(s, 500, 'Internal Error', e)
                except Exception as e:
                    traceback.print_exc()
                    if not status_sent:
                        send_status(s, 500, 'Internal Error', e)


if __name__ == '__main__':
    main()

#
# locathost/tracerout -> calls examp.html ->
# input an address into html field ->
# python calls tracerout and creates a list of addresses->
# calls api site and creates a map with the coordinates ->
#

# cd C:\Users\Raya\Documents\Rashel-\network-course-master
# Python -m http.server --bind-port 8080
# vim: expandtab tabstop=4 shiftwidth=4

# 172.16.255.254
