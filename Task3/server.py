import socket
import time
import datetime
import dns.message
import dns.query
import dns.rcode
import dns.rdatatype
import dns.flags
from dns.exception import DNSException, Timeout

# ========== CONFIG ==========
HOST = "10.0.0.5"
PORT = 53
ROOT_SERVERS = [
    "198.41.0.4",      # a.root-servers.net
    "199.9.14.201",    # b.root-servers.net
    "192.33.4.12",     # c.root-servers.net
]
# ============================

dns_cache = {}
dns_cache["responses"] = {}

print(f"Custom DNS Resolver running on {HOST}:{PORT}")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

def log_event(domain, mode, server_ip, step, rtype, rtt, cache):
    with open("dns_log.csv", "a") as f:
        f.write(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{domain},{mode},{server_ip},{step},{rtype},{round(rtt,3)},{cache}\n"
        )

def update_cache(response):
    """Store additional A records in cache"""
    if response.additional:
        for rrset in response.additional:
            for rr in rrset:
                if rr.rdtype == dns.rdatatype.A:
                    dns_cache[str(rrset.name)] = rr.address

def recursive_lookup(name, qtype):
    """Perform recursive lookup manually"""
    for root_ip in ROOT_SERVERS:
        try:
            query = dns.message.make_query(name, qtype)
            start = time.time()
            resp = dns.query.udp(query, root_ip, timeout=3)
            rtt = (time.time() - start) * 1000
            log_event(name, "Recursive", root_ip, "Root", "Referral", rtt, "MISS")

            if resp.answer:
                return resp

            if resp.additional:
                update_cache(resp)
                for rrset in resp.additional:
                    for rr in rrset:
                        if rr.rdtype == dns.rdatatype.A:
                            next_ip = rr.address
                            try:
                                query2 = dns.message.make_query(name, qtype)
                                start2 = time.time()
                                resp2 = dns.query.udp(query2, next_ip, timeout=3)
                                rtt2 = (time.time() - start2) * 1000
                                log_event(name, "Recursive", next_ip, "TLD/Auth", "Response", rtt2, "MISS")
                                if resp2.answer:
                                    return resp2
                            except Exception:
                                continue
        except Exception:
            continue
    return None

# Write CSV header
with open("dns_log.csv", "w") as f:
    f.write("Timestamp,Domain,Mode,Server_IP,Step,Response Type,RTT(ms),Cache Status\n")

while True:
    try:
        data, addr = sock.recvfrom(4096)
        client_ip, _ = addr

        req = dns.message.from_wire(data)
        q = req.question[0]
        domain = q.name.to_text()
        qtype = q.rdtype

        # CACHE CHECK
        cache_hit = dns_cache["responses"].get(domain)
        if cache_hit:
            resp = dns.message.from_wire(cache_hit)
            resp.id = req.id
            sock.sendto(resp.to_wire(), addr)
            log_event(domain, "Recursive", "-", "Cache", "Response", 0, "HIT")
            continue

        # Perform Recursive Lookup
        response = recursive_lookup(domain, qtype)
        if response:
            response.id = req.id
            response.flags |= dns.flags.QR
            response.flags |= dns.flags.RA
            sock.sendto(response.to_wire(), addr)
            dns_cache["responses"][domain] = response.to_wire()
        else:
            fail = dns.message.make_response(req)
            fail.set_rcode(dns.rcode.SERVFAIL)
            sock.sendto(fail.to_wire(), addr)
    except KeyboardInterrupt:
        print("\nServer shutting down.")
        break
    except Exception as e:
        print(f"Error: {e}")
        continue