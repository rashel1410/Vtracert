# -*- coding: utf-8 -*-
""" Constants """
## @file constants.py

#
# For http server
#
BLOCK_SIZE = 1024
CRLF = '\r\n'
CRLF_BIN = CRLF.encode('utf-8')
DEFAULT_HTTP_PORT = 8080
HTTP_SIGNATURE = 'HTTP/1.1'
MAX_HEADER_LENGTH = 4096
MAX_NUMBER_OF_HEADERS = 100
MAX_TIME = 5
MIME_MAPPING = {
    'xml': 'text/xml',
    'html': 'text/html',
    'png': 'image/png',
    'txt': 'text/plain',
}

#
# For my tracert
#
ID = '1234'
DATA_LEN = 64
ETH_TYPE = '0800'
HEADER_LEN = '45'
DIFF_FIELD = '00'
TOTAL_LEN = '003c'
IDENTIFICATION = '3db1'
FRAGM_OFFSET = '0000'
IP_PROT = '01'
ICMP_ECHO_TYPE = '08'
ICMP_CODE = '00'

#
# For ipconfigMac
#
START = 24
END = 41
DEFAULT_IFACE_PLACE = 3

#
# For reply
#
TTL_EXCEEDED = '0b'
ECHO_REPLY = '00'
ICMP = '01'

#
# For text tracert
#
TIME = 5
MAX_HOPS = 30

#
# For addresses
#
LOCALHOST = '127.0.0.1'


# vim: expandtab tabstop=4 shiftwidth=4
