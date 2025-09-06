import os
from pathlib import Path
import socket
import logging
from typing import Any
from linux_playground.utils.dir_utils.config_utils import config_load_yaml
from linux_playground.utils.operating_system_utils.os_utils import is_windows_os


# Host to listen to, In that case it's my machine 
WIN_OS = 'nt'

def packet_sniffing_script_root_prvlg(host_ip):
    # creating raw socket by OS Linux or Windows.
    print(f"[main] Current HOST: {host_ip}")
    if is_windows_os():
        socket_porotocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, type=socket.SOCK_RAW, proto=socket_protocol)
    sniffer.bind((host_ip, 0))
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    if is_windows_os():
        sniffer.ioctl(socket.SOCKET_RCVALL, socket.RCVALL_ON)

    # read one packet 
    raw_bytes_data: bytes = sniffer.recvfrom(65565)
    logging.info(f"raw_bytes_data: {raw_bytes_data}")


    # if on WIN OS turn off promiscuous mode
    if is_windows_os():
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
    
    return raw_bytes_data
    


if __name__ == '__main__':
    config_data: Any = config_load_yaml(config_file="ip_sniffing_config.yaml")
    targets = config_data.get("targets")
    host_ip = targets[1]['ip']
    target_ip = targets[2]['ip']

    raw_bytes_value: bytes = packet_sniffing_script_root_prvlg(host_ip)
    print(f"raw_bytes_value: {raw_bytes_value}")
    