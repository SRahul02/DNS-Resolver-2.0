import sys
from scapy.all import PcapReader, DNSQR, DNS

# --- Usage ---
# python extract_domains.py <input_pcap_file> <output_domain_list>
# Example: python extract_domains.py PCAP_1_H1.pcap h1_domains.txt

if len(sys.argv) != 3:
    print("Usage: python extract_domains.py <input_pcap_file> <output_domain_list>")
    sys.exit(1)

pcap_file = sys.argv[1]
output_file = sys.argv[2]

domains = set() # Use a set to avoid duplicates
packet_count = 0
dns_count = 0
error_count = 0

print(f"--- Starting to process {pcap_file} ---")
print("Reading packet-by-packet...")

try:
    # Use PcapReader to read one packet at a time (much faster)
    with PcapReader(pcap_file) as pcap_reader:
        for pkt in pcap_reader:
            packet_count += 1

            try:
                # Check for DNS Query
                if pkt.haslayer(DNSQR):
                    dns_count += 1
                    domain = pkt[DNSQR].qname.decode('utf-8')
                    if domain.endswith('.'):
                        domain = domain[:-1] # Remove trailing dot
                    domains.add(domain)

            except Exception as e:
                # This will catch any errors on a single malformed packet
                error_count += 1

            # --- This is your continuous feedback ---
            # Print a status update every 50,000 packets
            if packet_count % 50000 == 0:
                print(f" ...Processed {packet_count} packets...")

    print(f"--- Finished! ---")
    print(f"Total packets scanned: {packet_count}")
    print(f"Total DNS queries found: {dns_count}")
    print(f"Total packet processing errors: {error_count}")

    # Write the unique domains to the output file
    with open(output_file, 'w') as f:
        for d in sorted(list(domains)):
            f.write(f"{d}\n")

    print(f"Successfully extracted {len(domains)} unique domains to {output_file}")

except FileNotFoundError:
    print(f"Error: PCAP file not found at {pcap_file}")
except Exception as e:
    print(f"An error occurred: {e}")