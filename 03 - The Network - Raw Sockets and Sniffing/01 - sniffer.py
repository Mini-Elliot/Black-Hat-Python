import socket
import os
import sys

# Host to listen on
host = "192.168.0.196"  # Replace with your local IP

def main():
    if os.name == "nt":
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    try:
        # Create a raw socket and bind it to the public interface
        sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
        sniffer.bind((host, 0))

        # Include the IP headers in the capture
        sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        # If on Windows, enable promiscuous mode
        if os.name == "nt":
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

        print("[*] Sniffer started. Waiting for packets...\n")

        try:
            # Capture a single packet
            raw_data, addr = sniffer.recvfrom(65565)
            print(f"[+] Packet received from {addr}")
            print(f"[+] Raw Data:\n{raw_data.hex()}")
        except KeyboardInterrupt:
            print("\n[*] Interrupted by user.")

        # If on Windows, disable promiscuous mode
        if os.name == "nt":
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

    except PermissionError:
        print("[-] Permission denied. Run as administrator/root.")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
