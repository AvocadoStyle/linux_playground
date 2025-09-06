import os
import socket

from linux_playground.utils.operating_system_utils.os_utils import is_windows_os

# Host to listen to, In that case it's my machine 
HOST = '192.168.1.18'
WIN_OS = 'nt'

def main():
    # creating raw socket by OS Linux or Windows.
    print(f"[main] Current HOST: {HOST}")
    if is_windows_os():
        socket_porotocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, type=socket.SOCK_RAW, proto=socket_protocol)
    sniffer.bind((HOST, 0))
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    if is_windows_os():
        sniffer.ioctl(socket.SOCKET_RCVALL, socket.RCVALL_ON)

    # read one packet 
    print(sniffer.recvfrom(65565))

    # if on WIN OS turn off promiscuous mode
    if is_windows_os():
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
    


if __name__ == '__main__':
    main()