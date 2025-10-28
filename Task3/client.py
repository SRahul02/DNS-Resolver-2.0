from scapy.utils import PcapReader
from scapy.layers.dns import DNS
from datetime import datetime
import socket
import struct
import os
import time
import csv

pcap_files = [
    "PCAP_1_H1.pcap",
    "PCAP_2_H2.pcap",
    "PCAP_3_H3.pcap",
    "PCAP_4_H4.pcap"
]
host_names = ["H1", "H2", "H3", "H4"]

server_ip = "10.0.0.5"
server_port = 53

log_file = "client_log.csv"
with open(log_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Host", "Domain", "Size(Bytes)", "Latency(ms)", "Status"])

dns_pkts = []
total_all = 0
print("\n========== Reading PCAPs ==========")

for idx, pcap_file in enumerate(pcap_files):
    host = host_names[idx]
    if not os.path.isfile(pcap_file):
        print(f"[!] File not found: {pcap_file}")
        continue

    print(f"\n[{host}] Reading {pcap_file} ...")
    start = time.time()
    count = 0
    dns_count = 0
    with PcapReader(pcap_file) as pcap:
        for pkt in pcap:
            count += 1
            if pkt.haslayer(DNS) and pkt[DNS].qr == 0:
                seq_id = f"{total_all % 100:02d}"
                timestamp = datetime.now().strftime("%H%M%S")
                cstm_hdr = (timestamp + seq_id).encode()
                dns_pkts.append({
                    "custom_header": cstm_hdr,
                    "original_packet": pkt[DNS],
                    "host": host
                })
                dns_count += 1
                total_all += 1

            if count % 50000 == 0:
                print(f"[{host}] Processed {count} packets... Found {dns_count} DNS queries so far.")

    elapsed = time.time() - start
    print(f"[{host}] Completed. Total packets: {count}, DNS queries: {dns_count}, Time: {elapsed:.2f}s")

print(f"\ Total packets scanned across all files: {total_all}\n")

# === Connect to server ===
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((server_ip, server_port))
print(f"[+] Connected to custom DNS resolver at {server_ip}:{server_port}\n")

stats = {h: {"success": 0, "fail": 0, "latencies": [], "bytes_sent": 0} for h in host_names}

# === Send packets ===
for i, pkt in enumerate(dns_pkts, 1):
    host = pkt["host"]
    packet_to_send = pkt['custom_header'] + bytes(pkt['original_packet'])
    size = len(packet_to_send)
    stats[host]["bytes_sent"] += size

    domain = pkt["original_packet"].qd.qname.decode() if pkt["original_packet"].qd else "N/A"
    print(f"[{host}] Sending packet {i}/{len(dns_pkts)} {domain}")

    try:
        start_time = time.time()
        client.sendall(struct.pack("!I", size) + packet_to_send)

        raw_size = client.recv(4)
        if not raw_size:
            stats[host]["fail"] += 1
            print(" No response")
            status = "FAIL"
            latency = 0
        else:
            resp_size = struct.unpack("!I", raw_size)[0]
            _ = client.recv(resp_size)
            latency = (time.time() - start_time) * 1000
            stats[host]["latencies"].append(latency)
            stats[host]["success"] += 1
            status = "SUCCESS"
            print(f"Response received ({latency:.2f} ms)")

        with open(log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                host, domain, size, f"{latency:.2f}", status
            ])

    except Exception as e:
        stats[host]["fail"] += 1
        print(f" Error: {e}")

print("\n======== Summary ========")
for host in host_names:
    success = stats[host]["success"]
    fail = stats[host]["fail"]
    avg_latency = sum(stats[host]["latencies"]) / len(stats[host]["latencies"]) if stats[host]["latencies"] else 0
    total_bytes = stats[host]["bytes_sent"]
    total_time_sec = sum(stats[host]["latencies"]) / 1000 if stats[host]["latencies"] else 1
    throughput = total_bytes / total_time_sec if total_time_sec > 0 else 0

    print(f"{host}: Success={success}, Fail={fail}, Avg Latency={avg_latency:.2f} ms, Throughput={throughput/1024:.2f} KB/s")

client.close()
print("\ All packets sent. Connection closed.")
print(f" Log saved to {log_file}")