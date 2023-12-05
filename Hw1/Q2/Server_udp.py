from socket import *
from collections import Counter


def transform_udp(client_data):
    counted = Counter(client_data)
    return client_data.upper()[::-1] + " , " + counted.most_common()[0][0].upper()


udp_socket = socket(AF_INET, SOCK_DGRAM)
udp_socket.bind(("", 9001))
print("UDP server started")

while True:
    data, addr = udp_socket.recvfrom(1024)
    if data.decode() == "exit" or not data:
        print(f"udp client with address {addr} disconnected")
    udp_response = transform_udp(data.decode())
    udp_socket.sendto(udp_response.encode(), addr)
