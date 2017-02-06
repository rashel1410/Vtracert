#!/usr/bin/python

def main():
    if len(sys.argv) > 1:
        iface = sys.argv[1]
    else:
        iface = gcap.GCap.get_interfaces()[0]['name']

    with gcap.GCap(iface=iface) as cap:
        dst = '52:54:00:12:34:50'
        src = '52:54:00:12:34:56'
        type = 0x1000
        cap.send_packet(
            hexstring_to_binary(dst, sep=':') +
            hexstring_to_binary(src, sep=':') +
            int_to_binary(type) +
            'testing 1 2 3'.encode('ascii')
        )


if __name__ == '__main__':
    main()