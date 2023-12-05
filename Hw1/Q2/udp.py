from socket import *
server_name = "127.0.0.1"
server_port = 9001

client_socket = socket(AF_INET, SOCK_DGRAM)

message = input("input the udp Message")
while message != "exit":
    client_socket.sendto(message.encode(), (server_name, server_port))
    modified_message, server_address = client_socket.recvfrom(1024)
    print("From server:", modified_message.decode())
    message = input("input the udp Message")

client_socket.sendto(message.encode(), (server_name, server_port))

