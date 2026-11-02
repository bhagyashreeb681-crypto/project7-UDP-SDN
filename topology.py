#!/usr/bin/env python3

from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel


def create_topology():

    net = Mininet(
        controller=None,
        switch=OVSSwitch
    )

    print("*** Adding remote SDN controller")
    net.addController(
        "c0",
        controller=RemoteController,
        ip="127.0.0.1",
        port=6653
    )

    print("*** Adding hosts")
    h1 = net.addHost("h1", ip="10.0.0.1/24")
    h2 = net.addHost("h2", ip="10.0.0.2/24")

    print("*** Adding OpenFlow switch")
    s1 = net.addSwitch(
        "s1",
        protocols="OpenFlow13"
    )

    print("*** Creating links")
    net.addLink(h1, s1)
    net.addLink(h2, s1)

    print("*** Starting network")
    net.start()

    print("*** Testing connectivity")
    net.pingAll()

    print("*** Starting Mininet CLI")
    CLI(net)

    print("*** Stopping network")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    create_topology()
