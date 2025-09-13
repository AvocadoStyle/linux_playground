from typing import Any
from linux_playground.python_playground.sniffers.ip_sniffer.packet_sniffing_win_linux import packet_sniffing_script_root_prvlg
from linux_playground.python_playground.sniffers.ip_sniffer.sniffer_decoder.sniffer_decoder_ip_struct import IpHdrDecoder
from linux_playground.utils.dir_utils.config_utils import config_load_yaml


def continuesly_sniffing(host_ip: str):
    i = 0
    while True:
        print(f"num: {i}")
        raw_bytes_value: bytes = packet_sniffing_script_root_prvlg(host_ip=host_ip)[0]
        print(f"raw_bytes_value: {raw_bytes_value}")
        ip_hdr_decoded = IpHdrDecoder(buffer=raw_bytes_value)
        print(f"{ip_hdr_decoded.ip_src} -> {ip_hdr_decoded.ip_dst} prot_name: {ip_hdr_decoded.protocol_name}")
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
    target_ip = targets[2]['ip']
    continuesly_sniffing(host_ip=host_ip)


