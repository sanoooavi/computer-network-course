from socket import *
server_name = "127.0.0.1"
server_port = 12000

client_socket = socket(AF_INET, SOCK_DGRAM)

message = input("input the udp Message")
while message != "exit":
    client_socket.sendto(message.encode(), (server_name, server_port))
    modified_message, server_address = client_socket.recvfrom(2048)
    print("From server:", modified_message.decode())
    message = input("input the udp Message")

client_socket.sendto(message, (server_name, server_port))
client_socket.close()

