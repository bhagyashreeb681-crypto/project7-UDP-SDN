import socket

HOST = "0.0.0.0"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))

print("UDP Server started...")
print("Waiting for packets...")

received_packets = set()

while True:
    data, address = server.recvfrom(1024)
    message = data.decode()

    if message == "STOP":
        print("Server stopped.")
        break

    sequence_number = int(message)
    received_packets.add(sequence_number)

    print("Received packet:", sequence_number)

    ack = f"ACK:{sequence_number}"
    server.sendto(ack.encode(), address)

print("Total packets received:", len(received_packets))
server.close()
