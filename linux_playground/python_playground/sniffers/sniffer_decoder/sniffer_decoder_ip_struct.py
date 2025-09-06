import os
import socket
import struct
from typing import Any

from linux_playground.python_playground.sniffers.sniffer.packet_sniffing_windows_linux import packet_sniffing_script_root_prvlg
from linux_playground.utils.dir_utils.config_utils import config_load_yaml

class IpHdrDecoder:
    def __init__(self, buffer: bytes):
        """
        Decode the IP Headers
        :param buffer: is the buffer bytes that we're getting from the inspection.
        :ivar _buffer: buffer saved
        """
        self._buffer: bytes = buffer
        self.header = struct.unpack('<BBHHHBBHII', self._buffer[:20])
        self.version = self.header[0] >> 4 # gets the lil-endian msb of the chunk. 
        self.hdr_len = self.header[0] & 0x0F # gets the lsb.
        self.tos = self.header[1]
        self.total_len = self.header[2]
        self.id = self.header[3]
        self.fragment_offset = self.header[4]
        self.ttl = self.header[5]
        self.protocol = self.header[6]
        self.cksum = self.header[7]
        self.src = self.header[8]
        self.dst = self.header[9]
        self.ip_src = socket.inet_ntoa(struct.pack('I', self.src))
        self.ip_dst = socket.inet_ntoa(struct.pack('I', self.dst))


if __name__ == '__main__':
    current_file_path = os.path.join(os.path.dirname(__file__), 'ip_sniffing_config.yaml')
    config_data: Any = config_load_yaml(current_file_path)
    targets: list = config_data.get("targets")
    host_ip: str = targets[1]['ip']
    target_ip: str = targets[2]['ip']

    raw_bytes_value: bytes = packet_sniffing_script_root_prvlg(host_ip)[0]
    print(f"raw_bytes_value: {raw_bytes_value}")
    ip_hdr_dec = IpHdrDecoder(buffer=raw_bytes_value)
    print(ip_hdr_dec.ip_src)
    print(ip_hdr_dec.ip_dst)