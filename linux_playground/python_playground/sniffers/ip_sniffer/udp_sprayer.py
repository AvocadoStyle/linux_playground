import socket
import ipaddress


def udp_sender(subnet: str = '192.168.1.0/24', message: str = "hey"):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sender:
        for ip in ipaddress.ip_network(subnet).hosts():
            udp_sender.sendto(bytes(message, 'utf-8'), (str(ip), 65212))
