from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

class CustomTopo(Topo):
    
    def build(self):
        # Hosts
        h1 = self.addHost('H1', ip='10.0.0.1/24')
        h2 = self.addHost('H2', ip='10.0.0.2/24')
        h3 = self.addHost('H3', ip='10.0.0.3/24')
        h4 = self.addHost('H4', ip='10.0.0.4/24')
        dns = self.addHost('DNS', ip='10.0.0.5/24')

        # Switches
        s1 = self.addSwitch('S1')
        s2 = self.addSwitch('S2')
        s3 = self.addSwitch('S3')
        s4 = self.addSwitch('S4')

        # Host-to-Switch Links
        self.addLink(h1, s1, bw=100, delay='2ms')
        self.addLink(h2, s2, bw=100, delay='2ms')
        self.addLink(h3, s3, bw=100, delay='2ms')
        self.addLink(h4, s4, bw=100, delay='2ms')
        self.addLink(dns, s2, bw=100, delay='1ms')

        # Switch-to-Switch
        self.addLink(s1, s2, bw=100, delay='5ms')
        self.addLink(s2, s3, bw=100, delay='8ms')
        self.addLink(s3, s4, bw=100, delay='10ms')

def run():
    topo = CustomTopo()
    net = Mininet(topo=topo, link=TCLink) # Using TCLink for bw and delay to work.
    
    net.start()
    
    print("\n*** Testing network connectivity (Task A) ***")
    net.pingAll() # Proof of successful connectivity
    
    print("\n*** Running Mininet CLI ***")
    print("You can now test connectivity, e.g., 'h1 ping h4'.")
    print("Type 'exit' to stop the simulation.")
    CLI(net)
    
    print("*** Stopping network ***")
    net.stop()

if __name__ == '__main__': # Tells Python to run the 'run()' function if the script is executed directly.
    setLogLevel('info')
    run()
