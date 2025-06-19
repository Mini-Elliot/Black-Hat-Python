import socket
import os
import struct
from ctypes import *

# Host to listen on
host = "192.168.0.187"

# Define the IP header using ctypes
class IP(Structure):
    _fields_ = [
        ("ihl", c_ubyte, 4),
        ("version", c_ubyte, 4),
        ("tos", c_ubyte),
        ("len", c_ushort),
        ("id", c_ushort),
        ("offset", c_ushort),
        ("ttl", c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum", c_ushort),
        ("src", c_ulong),
        ("dst", c_ulong)
    ]

    def __new__(cls, socket_buffer=None):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        # Map protocol constants to names
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        # Convert packed IP addresses to readable strings
        self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))

        # Set human-readable protocol name
        self.protocol = self.protocol_map.get(self.protocol_num, str(self.protocol_num))


def main():
    if os.name == "nt":
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    try:
        # Create a raw socket and bind it to the host
        sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
        sniffer.bind((host, 0))

        # Include IP headers in captured packets
        sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        # If on Windows, enable promiscuous mode
        if os.name == "nt":
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

        print(f"[*] Listening on {host}... Press Ctrl+C to stop.\n")

        while True:
            # Read a packet
            raw_buffer = sniffer.recvfrom(65565)[0]

            # Create an IP header from the first 20 bytes
            ip_header = IP(raw_buffer[0:20])

            # Display protocol and addresses
            print(f"Protocol: {ip_header.protocol} | {ip_header.src_address} -> {ip_header.dst_address}")

    except KeyboardInterrupt:
        print("\n[*] Shutting down...")

        # If on Windows, disable promiscuous mode
        if os.name == "nt":
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
    except PermissionError:
        print("[-] Error: You must run this script as administrator/root.")
    except Exception as e:
        print(f"[-] Unexpected error: {e}")


if __name__ == "__main__":
    main()
