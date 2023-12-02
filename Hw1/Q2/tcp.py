from socket import *
server_name = "127.0.01"
server_port = 12000
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((server_name, server_port))
message = input("input the tcp Message")
while message != "exit":
    client_socket.send(message.encode())
    modified_message = client_socket.recv(1024)
    print("From Server : " + modified_message.decode())

client_socket.send(message.encode())
client_socket.close()
