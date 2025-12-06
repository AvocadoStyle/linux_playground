import os
import socket
import struct
from typing import Any, Optional

from linux_playground.utils.constants import IP_PROTOCOL_MAP
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
        self.protocol_map = {IP_PROTOCOL_MAP.ICMP.value: IP_PROTOCOL_MAP.ICMP.name,
                             IP_PROTOCOL_MAP.TCP.value: IP_PROTOCOL_MAP.TCP.name,
                             IP_PROTOCOL_MAP.TCP.value: IP_PROTOCOL_MAP.TCP.name}
        self.protocol_name: Optional[str] = None
        try:
            self.set_protocol()
        except Exception as e:
            print(f"[error] protocol did not set properly")
            raise e

    
    def set_protocol(self):
        self.protocol_name = self.protocol_map[self.protocol] 


# if __name__ == '__main__':
#     # getting the configfile data
#     IP_CONFIG_FILE_NAME = 'ip_sniffing_config.yaml'
#     # checking if the configfile data is exists
#     from pathlib import Path
#     current_file_path = Path(__file__)
#     main_directory = current_file_path.parent.parent
#     ip_config_file_path = main_directory.joinpath('configuration', 'ip_sniffing_config.yaml')
#     assert ip_config_file_path.is_file()
#     ip_config_file_path = str(ip_config_file_path)
#     config_data: Any = config_load_yaml(ip_config_file_path)
#     # gets the data from the file
#     targets: list = config_data.get("targets")
#     host_ip: str = targets[1]['ip']
#     target_ip: str = targets[2]['ip']

#     raw_bytes_value: bytes = packet_sniffing_script_root_prvlg(host_ip)[0]
#     print(f"raw_bytes_value: {raw_bytes_value}")
#     ip_hdr_dec = IpHdrDecoder(buffer=raw_bytes_value)
#     print(ip_hdr_dec.ip_src)
#     print(ip_hdr_dec.ip_dst)