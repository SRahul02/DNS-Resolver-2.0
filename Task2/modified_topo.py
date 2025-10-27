from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.nodelib import NAT

class CustomTopo(Topo):

    def build(self):

        natIP = '10.0.0.254'

        # Add hosts
        h1 = self.addHost('H1', ip='10.0.0.1/24', defaultRoute=f'via {natIP}')
        h2 = self.addHost('H2', ip='10.0.0.2/24', defaultRoute=f'via {natIP}')
        h3 = self.addHost('H3', ip='10.0.0.3/24', defaultRoute=f'via {natIP}')
        h4 = self.addHost('H4', ip='10.0.0.4/24', defaultRoute=f'via {natIP}')
        dns = self.addHost('DNS', ip='10.0.0.5/24', defaultRoute=f'via {natIP}')

        # Add switches
        s1 = self.addSwitch('S1')
        s2 = self.addSwitch('S2')
        s3 = self.addSwitch('S3')
        s4 = self.addSwitch('S4')

        # Add host-to-switch links with specified parameters
        # (bw=100Mbps)
        self.addLink(h1, s1, bw=100, delay='2ms')
        self.addLink(h2, s2, bw=100, delay='2ms')
        self.addLink(h3, s3, bw=100, delay='2ms')
        self.addLink(h4, s4, bw=100, delay='2ms')
        self.addLink(dns, s2, bw=100, delay='1ms')

        # Add switch-to-switch links with specified parameters
        # (bw=100Mbps)
        self.addLink(s1, s2, bw=100, delay='5ms')
        self.addLink(s2, s3, bw=100, delay='8ms')
        self.addLink(s3, s4, bw=100, delay='10ms')

        self.addHost('nat', ip=natIP, cls=NAT, inNamespace=False)
        self.addLink('nat', s2)

def run():
    "Create and run the network."
    topo = CustomTopo()

    # We MUST use TCLink for bandwidth (bw) and delay to work.
    net = Mininet(topo=topo, link=TCLink)
    print("*** Starting network ***")
    net.start()

    print("*** Configuring host DNS (resolv.conf) ***")
    for host in net.hosts:
        # Skip the NAT device, which isn't a "real" host
        if host.name == 'nat':
            continue
        # Set 8.8.8.8 (Google) as the nameserver for all hosts
        host.cmd(f'echo "nameserver 8.8.8.8" > /etc/resolv.conf')
        print(f"   ...configured DNS for {host.name}")

    print("\n*** Testing network connectivity (Task A) ***")
    # This pingAll() demonstrates successful connectivity for Task A.
    net.pingAll()

    print("*** Running CLI ***")
    CLI(net)

    print("*** Stopping network ***")
    net.stop()

if __name__ == '__main__':
    # Tells Python to run the 'run()' function if the script is executed directly.
    setLogLevel('info')
    run()