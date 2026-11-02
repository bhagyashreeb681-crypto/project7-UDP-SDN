import socket
import time

SERVER_IP = "10.0.0.2"
SERVER_PORT = 5000
TOTAL_PACKETS = 20
MAX_RETRIES = 3

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(2)

received_acks = set()
total_attempts = 0
total_retries = 0

start_time = time.time()

for seq in range(1, TOTAL_PACKETS + 1):

    acknowledged = False

    for attempt in range(MAX_RETRIES):

        total_attempts += 1

        if attempt > 0:
            total_retries += 1

        client.sendto(str(seq).encode(), (SERVER_IP, SERVER_PORT))
        print("Sent packet:", seq)

        try:
            data, address = client.recvfrom(1024)
            ack = data.decode()

            if ack == f"ACK:{seq}":
                print("Received:", ack)
                received_acks.add(seq)
                acknowledged = True
                break

        except socket.timeout:
            print("Timeout! Retrying packet:", seq)

    if not acknowledged:
        print("Packet failed:", seq)

    time.sleep(0.2)

client.sendto(b"STOP", (SERVER_IP, SERVER_PORT))

end_time = time.time()

successful = len(received_acks)
failed = TOTAL_PACKETS - successful

recovery_percentage = (successful / TOTAL_PACKETS) * 100

print("\n------ EXPERIMENT RESULTS ------")
print("Total packets:", TOTAL_PACKETS)
print("Total transmission attempts:", total_attempts)
print("Total retries:", total_retries)
print("Successful packets:", successful)
print("Failed packets:", failed)
print("Recovery percentage:", recovery_percentage, "%")
print("Execution time:", round(end_time - start_time, 2), "seconds")

client.close()
