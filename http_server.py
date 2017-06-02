#!/usr/bin/python
""" http server """
## @file http_server.py A server on http protocol

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


## Parsing
#@ no params
#@ returns program's arguments
#
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
        '--mac',
        default='GET_MAC',
        help='MAC address of your computer, without - separation',
    )
    parser.add_argument(
        '--debug',
        default='DONT',
        help='--debug D, if you want to see the debug prints in a file in VTracert',
    )
    parser.add_argument(
        '--base',
        default='.',
        help='Base directory to search fils in, default: %(default)s',
    )
    args = parser.parse_args()
    args.base = os.path.normpath(os.path.realpath(args.base))
    return args
    

## Send error status
#@ param s - socket
#@ param code (int)  -the error code
#@ param message (string) - error message
#@ param extra
#
# Used for errors
#
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


## Creates an xml
#@ param ip (string) - ip address
#@ param stat (string) - HOP / REACH / TIMEOUT
#
def create_xml(ip,stat, delta, run):

    root = et.Element('root')
    print delta
    print run
    cont = et.SubElement(root, 'result', ipAddr = ip, status = stat, delta_time = str(delta), run_time = str(run))
    return et.tostring(root)
    

## main
#
def main():

    RUN_TIME = 0
    args = parse_args()
    sys.stderr.write( 'start...' )
    
    if args.debug == 'D':
        to_file = True
    else:
        to_file = False

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

                    if uri[:7] == '/trace?':
                        parse = urlparse.urlparse(uri)
                        param = urlparse.parse_qs(parse.query).values()
                        ip_or_dns = param[0][0]
                        ttl = int(param[1][0])
                        hop = ''
                        status = 'NONE'
                        last_delta = RUN_TIME
                        status, hop, RUN_TIME = my_tracert(ip_or_dns, ttl, constants.MAX_TIME, args.mac, to_file)
                        sys.stderr.write( "TTL "+str(ttl)+'\n')
                        sys.stderr.write( status+'\n')
                        #
                        # hex ip to regular ip
                        #
                        ip = ''
                        index = 0
                        part = ''
                        for i in range(len(hop)/2):
                            part = hop[index:index+2]
                            ip += str(int(part,16)) + '.'
                            index += 2
                        ip = ip[:-1]
                        delta = RUN_TIME - last_delta
                        sys.stderr.write(ip+'\n\n')
                        sys.stderr.write(str(delta)+'\n\n')
                        sys.stderr.write(str(RUN_TIME)+'\n\n')
                        sys.stderr.write(str(last_delta)+'\n\n')
                        out = create_xml(ip, status, delta, RUN_TIME)
                        util.send_all(
                            s,
                            (
                                    (
                                        '%s 200 OK\r\n'
                                        'Content-Length: %s\r\n'
                                        'Content-Type: %s\r\n'
                                        '\r\n'
                                    ) % (
                                        constants.HTTP_SIGNATURE,
                                        len(out),
                                        constants.MIME_MAPPING.get('xml'),
                                    )
                            ).encode('utf-8')
                        )
                        util.send_all(s, out)
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
                                        # => goes to constants.MIME_MAPPING.
                                        #
                                        constants.HTTP_SIGNATURE,
                                        os.fstat(f.fileno()).st_size,
                                        constants.MIME_MAPPING.get(
                                            os.path.splitext(
                                                file_name
                                            )[1].lstrip('.'),
                                            constants.MIME_MAPPING.get('http'),
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

# Python -m http.server --bind-port 8080
# vim: expandtab tabstop=4 shiftwidth=4
