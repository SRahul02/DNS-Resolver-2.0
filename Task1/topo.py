from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch

class CustomTopo(Topo):
    def build(self):
        # Add hosts
        h1 = self.addHost('H1', ip='10.0.0.1/24')
        h2 = self.addHost('H2', ip='10.0.0.2/24')
        h3 = self.addHost('H3', ip='10.0.0.3/24')
        h4 = self.addHost('H4', ip='10.0.0.4/24')
        dns = self.addHost('DNS', ip='10.0.0.5/24')

        # Add switches
        s1 = self.addSwitch('S1')
        s2 = self.addSwitch('S2')
        s3 = self.addSwitch('S3')
        s4 = self.addSwitch('S4')

        # Add host ↔ switch links (with bandwidth and delay)
        self.addLink(h1, s1, bw=100, delay='2ms')
        self.addLink(h2, s2, bw=100, delay='2ms')
        self.addLink(h3, s3, bw=100, delay='2ms')
        self.addLink(h4, s4, bw=100, delay='2ms')
        self.addLink(dns, s2, bw=100, delay='1ms')

        # Add switch ↔ switch links
        self.addLink(s1, s2, bw=100, delay='5ms')
        self.addLink(s2, s3, bw=100, delay='8ms')
        self.addLink(s3, s4, bw=100, delay='10ms')

def run():
    topo = CustomTopo()
    net = Mininet(topo=topo, link=TCLink, switch=OVSKernelSwitch, controller=None)
    net.start()
    print("*** Testing network connectivity ***")
    net.pingAll()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()