import socket
import os
import struct
import threading
import time
from ctypes import *
from netaddr import IPNetwork, IPAddress

# Host IP (your local machine's IP)
host = "192.168.0.187"
# Subnet to scan
subnet = "192.168.0.0/24"
# Secret message to validate ICMP response
magic_message = b"PYTHONRULES!"

# Define IP header with ctypes
class IP(Structure):
    _fields_ = [
        ("ihl",           c_ubyte, 4),
        ("version",       c_ubyte, 4),
        ("tos",           c_ubyte),
        ("len",           c_ushort),
        ("id",            c_ushort),
        ("offset",        c_ushort),
        ("ttl",           c_ubyte),
        ("protocol_num",  c_ubyte),
        ("sum",           c_ushort),
        ("src",           c_ulong),
        ("dst",           c_ulong)
    ]

    def __new__(cls, socket_buffer=None):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
        self.protocol = self.protocol_map.get(self.protocol_num, str(self.protocol_num))


# Define ICMP header with ctypes
class ICMP(Structure):
    _fields_ = [
        ("type",     c_ubyte),
        ("code",     c_ubyte),
        ("checksum", c_ushort),
        ("unused",   c_ushort),
        ("next_hop_mtu", c_ushort)
    ]

    def __new__(cls, socket_buffer):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass


# Send UDP packets to subnet with the magic message
def udp_sender(subnet, magic_message):
    time.sleep(2)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for ip in IPNetwork(subnet):
        try:
            sender.sendto(magic_message, (str(ip), 65212))
        except:
            pass


def main():
    if os.name == "nt":
        protocol = socket.IPPROTO_IP
    else:
        protocol = socket.IPPROTO_ICMP

    try:
        sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, protocol)
        sniffer.bind((host, 0))
        sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        if os.name == "nt":
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    except Exception as e:
        print(f"[-] Error initializing socket: {e}")
        return

    # Start UDP sender thread
    t = threading.Thread(target=udp_sender, args=(subnet, magic_message))
    t.start()

    try:
        while True:
            raw_buffer = sniffer.recvfrom(65565)[0]

            # Parse IP header
            ip_header = IP(raw_buffer[:20])

            if ip_header.protocol == "ICMP":
                offset = ip_header.ihl * 4
                icmp_buffer = raw_buffer[offset:offset + sizeof(ICMP)]

                icmp_header = ICMP(icmp_buffer)

                # Check for "Destination Unreachable - Port Unreachable"
                if icmp_header.type == 3 and icmp_header.code == 3:
                    if IPAddress(ip_header.src_address) in IPNetwork(subnet):
                        # Check if our magic message is in the payload
                        if raw_buffer[-len(magic_message):] == magic_message:
                            print(f"[+] Host Up: {ip_header.src_address}")

    except KeyboardInterrupt:
        print("\n[*] Stopping scan.")
        if os.name == "nt":
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


if __name__ == '__main__':
    main()
