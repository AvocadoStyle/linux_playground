import os
from pathlib import Path
import socket
import logging
import threading
from typing import Any
from linux_playground.python_playground.sniffers.ip_sniffer.sniffer_decoder.sniffer_decoder_icmp_struct import ICMPDecoder
from linux_playground.python_playground.sniffers.ip_sniffer.sniffer_decoder.sniffer_decoder_ip_struct import IpHdrDecoder
from linux_playground.python_playground.sniffers.ip_sniffer.udp_sprayer import udp_sender
from linux_playground.utils.constants import IP_PROTOCOL_MAP
from linux_playground.utils.dir_utils.config_utils import config_load_yaml
from linux_playground.utils.operating_system_utils.os_utils import is_windows_os
import ipaddress

# Host to listen to, In that case it's my machine 
WIN_OS = 'nt'

class Scanner:
    def __init__(self, host_ip: str, subnet: str, message: str):
        self.host_ip = host_ip
        self.subnet = subnet
        self.message = message
        print(f"[main] Current HOST: {host_ip}")
        self.sniffer = None
        self._sniffer_setup()
    
    def _sniffer_setup(self):
        if is_windows_os():
            logging.info(f"Running on Windows OS")
            socket_protocol = socket.IPPROTO_IP
        else:
            socket_protocol = socket.IPPROTO_ICMP
        logging.info(f"socket_protocol: {socket_protocol}")
        self.sniffer = socket.socket(socket.AF_INET, type=socket.SOCK_RAW, proto=socket_protocol)
        self.sniffer.bind((host_ip, 0))
        self.sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        if is_windows_os():
            self.sniffer.ioctl(socket.SOCKET_RCVALL, socket.RCVALL_ON)
    
    def sniff(self) -> bytes:
        # read one packet 
        raw_bytes_data: bytes = self.sniffer.recvfrom(65565)
        logging.info(f"raw_bytes_data: {raw_bytes_data}")

        # if on WIN OS turn off promiscuous mode
        if is_windows_os():
            self.sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

        return raw_bytes_data[0]

    def sniff_decoder(self):
        buffer: bytes = self.sniff()
        ip_hdr_decoded = IpHdrDecoder(buffer=buffer)
        print(f"{ip_hdr_decoded.ip_src} -> {ip_hdr_decoded.ip_dst} prot_name: {ip_hdr_decoded.protocol_name}")
        if ip_hdr_decoded.protocol_name == IP_PROTOCOL_MAP.ICMP.name:
            print(f"Version: {ip_hdr_decoded.version}")
            print(f"Header Length: {ip_hdr_decoded.hdr_len}")
            # Calculate ICMP packet start
            offset = ip_hdr_decoded.hdr_len * 4
            icmp_buffer = buffer[offset:offset + 8]
            icmp_hdr_decoded = ICMPDecoder(buffer=icmp_buffer)
            print(f"ICMP Type: {icmp_hdr_decoded.type}")
            print(f"ICMP Code: {icmp_hdr_decoded.code}")
            
            # checks if we can add the host as "up" target
            if icmp_hdr_decoded.code == 3 and icmp_hdr_decoded.type == 3:
                if ipaddress.ip_address(ip_hdr_decoded.ip_src) in ipaddress.IPv4Network(self.subnet):
                    if buffer[len(buffer) - len(self.message):] == bytes(self.message, 'utf-8'):
                        target = str(ip_hdr_decoded.ip_src)
                        if target != self.host_ip and target not in self.hosts_up:
                            self.hosts_up.add(target)
                            print(f"host up: {target}")
        print(f"total hosts: {self.hosts_up}")
                            
    def continuesly_sniffer_decoder(self):
        i = 0
        self.hosts_up = set([f'{str(self.host_ip)} *'])
        while True:
            print(f"index: {i}")
            self.sniff_decoder()
            i += 1
    

if __name__ == '__main__':
    IP_CONFIG_FILE_NAME = 'ip_sniffing_config.yaml'
    from pathlib import Path
    current_file_path = Path(__file__)
    main_directory = current_file_path.parent
    ip_config_file_path = main_directory.joinpath('configuration', IP_CONFIG_FILE_NAME)
    assert ip_config_file_path.is_file()
    ip_config_file_path = str(ip_config_file_path)
    config_data: Any = config_load_yaml(ip_config_file_path)

    targets = config_data.get("targets")
    host_ip = targets[1]['ip']
    host_ip_subnet = targets[1]['subnet']
    target_ip = targets[2]['ip']

    scanner = Scanner(host_ip=host_ip, subnet=host_ip_subnet, message="hey")
    t1 = threading.Thread(target=udp_sender)
    t1.start()
    scanner.continuesly_sniffer_decoder()

    
