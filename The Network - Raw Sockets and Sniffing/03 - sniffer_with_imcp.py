import socket
import os
import struct
from ctypes import *

# Host to listen on
host = "192.168.0.187"  # Change to your interface IP

# IP header definition
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
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
        self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))
        self.protocol = self.protocol_map.get(self.protocol_num, str(self.protocol_num))


# ICMP header definition
class ICMP(Structure):
    _fields_ = [
        ("type",         c_ubyte),
        ("code",         c_ubyte),
        ("checksum",     c_ushort),
        ("unused",       c_ushort),
        ("next_hop_mtu", c_ushort)
    ]

    def __new__(cls, socket_buffer):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass  # We don't need to process further in this example


def main():
    if os.name == "nt":
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    try:
        sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
        sniffer.bind((host, 0))

        # Include IP headers
        sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        # Enable promiscuous mode on Windows
        if os.name == "nt":
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

        print(f"[*] Sniffing on {host}...\n")

        while True:
            raw_buffer = sniffer.recvfrom(65565)[0]

            # Parse IP header
            ip_header = IP(raw_buffer[:20])
            print(f"\n[IP] {ip_header.protocol}: {ip_header.src_address} -> {ip_header.dst_address}")

            # If it's ICMP, parse the ICMP header
            if ip_header.protocol == "ICMP":
                offset = ip_header.ihl * 4
                buf = raw_buffer[offset:offset + sizeof(ICMP)]
                icmp_header = ICMP(buf)

                print(f"[ICMP] Type: {icmp_header.type} | Code: {icmp_header.code}")

    except KeyboardInterrupt:
        print("\n[*] Interrupted. Exiting...")

        if os.name == "nt":
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

    except PermissionError:
        print("[-] Permission denied. Run as Administrator/root.")

    except Exception as e:
        print(f"[-] Unexpected error: {e}")


if __name__ == "__main__":
    main()
