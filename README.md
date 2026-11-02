# PROJECT 7: UDP PACKET LOSS DETECTION AND RECOVERY USING SDN

## 1. Introduction

This project demonstrates UDP communication between two hosts using Python socket programming and Software-Defined Networking (SDN).

UDP does not guarantee packet delivery. This project uses acknowledgments, timeouts and retransmissions to improve delivery reliability.

## 2. Objectives

- Implement UDP client-server communication.
- Detect missing acknowledgments.
- Retransmit packets when acknowledgments are not received.
- Simulate packet loss.
- Integrate Mininet, Open vSwitch and an SDN controller.
- Monitor UDP traffic and install dynamic forwarding rules.
- Evaluate network performance.

## 3. Technologies Used

- Ubuntu Linux
- Python 3
- UDP socket programming
- Mininet
- Open vSwitch
- OpenFlow 1.3
- OS-Ken SDN Controller
- Linux Traffic Control (tc/netem)

## 4. Network Architecture

The network contains:

- H1: UDP client (10.0.0.1)
- H2: UDP server (10.0.0.2)
- S1: Open vSwitch
- C0: OS-Ken SDN controller

Both hosts communicate through the OpenFlow switch, which is connected to the SDN controller.

## 5. Implementation

### 5.1 UDP Client

The client sends 20 sequence-numbered UDP packets to the server.

It waits for an acknowledgment for each packet. If an acknowledgment is not received within the timeout period, the client retransmits the packet.

A maximum of three transmission attempts is allowed for each packet.

### 5.2 UDP Server

The server listens on UDP port 5000. It receives packets, records their sequence numbers and sends acknowledgments to the client.

### 5.3 SDN Controller

The OS-Ken controller uses OpenFlow 1.3.

It monitors UDP traffic directed to destination port 5000. After observing five matching UDP packets, it installs a higher-priority forwarding rule in the switch.

### 5.4 Mininet Topology

Mininet creates two hosts connected through one Open vSwitch. The switch connects to the remote SDN controller through port 6653.

## 6. Experimental Setup

Two experiments were conducted.

### Experiment 1: Normal Network

The client and server communicate without intentionally configured packet loss.

### Experiment 2: Simulated Packet Loss

Packet loss is configured on the outgoing interface of H1 using:

`tc qdisc add dev h1-eth0 root netem loss 30%`

This configures an approximate 30% packet-loss probability. The actual number of lost packets can vary between runs.

## 7. Experimental Results

### Experiment 1: Normal Network

| Metric | Result |
|---|---:|
| Total packets | 20 |
| Transmission attempts | 20 |
| Retries | 0 |
| Successful packets | 20 |
| Failed packets | 0 |
| Acknowledgment percentage | 100% |
| Execution time | 4.18 seconds |

### Experiment 2: Simulated Packet Loss

| Metric | Result |
|---|---:|
| Total packets | 20 |
| Transmission attempts | 31 |
| Retries | 11 |
| Successful packets | 18 |
| Failed packets | 2 |
| Recovery percentage | 90% |
| Execution time | 30.15 seconds |

## 8. SDN Flow Rule Verification

The switch flow table was checked using:

`sh ovs-ofctl -O OpenFlow13 dump-flows s1`

A priority-10 UDP forwarding rule was observed.

The rule matches:
- Source IP: 10.0.0.1
- Destination IP: 10.0.0.2
- UDP destination port: 5000

The switch forwards matching packets through port 2.

The flow-table evidence is saved in `flow_rules.txt`.

## 9. Observations

In the normal network, all 20 packets were acknowledged without retransmission.

During simulated packet loss, 11 additional transmission attempts were made. Eighteen packets were successfully acknowledged, while two remained unsuccessful after the maximum retry attempts.

The experiment demonstrates how timeout-based retransmission improves UDP delivery reliability.

The SDN controller also demonstrates UDP traffic monitoring and dynamic forwarding-rule installation.

## 10. Conclusion

The project demonstrates UDP client-server communication, acknowledgment-based retransmission, packet-loss simulation and SDN-based dynamic forwarding.

The recorded packet-loss experiment achieved 90% recovery. The controller successfully installed a higher-priority forwarding rule for matching UDP traffic.

## 11. Project Files

- `client.py` – UDP client.
- `server.py` – UDP server.
- `controller.py` – SDN controller.
- `topology.py` – Mininet topology.
- `results.txt` – Experimental results.
- `flow_rules.txt` – Switch flow-table evidence.

## 12. Future Enhancements

- Test different packet-loss probabilities.
- Evaluate additional network topologies.
- Add more hosts.
- Measure throughput and latency.
- Explore SDN-based rerouting and congestion management.
## 13. How to Run the Project

### Step 1: Start the SDN Controller

Open Terminal 1 and run:

```bash
cd ~/project7
source ~/osken-env/bin/activate
osken-manager controller.py
```

Keep the controller running.

### Step 2: Start the Mininet Topology

Open Terminal 2 and run:

```bash
cd ~/project7
sudo python3 topology.py
```

Wait until the `mininet>` prompt appears.

### Step 3: Start the UDP Server

At the `mininet>` prompt, run:

```bash
h2 python3 /home/bhagyashree/project7/server.py &
```

### Step 4: Run the UDP Client

```bash
h1 python3 /home/bhagyashree/project7/client.py
```

The client displays packet transmission, acknowledgments, retries, and experiment results.

### Step 5: Simulate Packet Loss

Before starting the server and client, configure approximate 30% packet loss:

```bash
h1 tc qdisc add dev h1-eth0 root netem loss 30%
```

Run the server and client again.

To remove the packet-loss condition:

```bash
h1 tc qdisc del dev h1-eth0 root
```

### Step 6: Inspect SDN Flow Rules

At the `mininet>` prompt:

```bash
sh ovs-ofctl -O OpenFlow13 dump-flows s1
```

This displays the flow rules installed in the Open vSwitch.
