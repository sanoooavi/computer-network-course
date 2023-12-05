import socket

# from message import Message
import threading


class Client:
    def __init__(self, cl_socket, username):
        self.cl_socket = cl_socket
        self.username = username
        self.group_chats = []

    def start(self):
        threading.Thread(target=self.send_messages).start()
        threading.Thread(target=self.receive_messages).start()

    def receive_messages(self):
        while True:
            # try:
            message = self.cl_socket.recv(1024).decode()
            if not message:
                self.cl_socket.close()
                break
            print(message)
        # except:
        #     self.socket.close()
        #     break

    def send_messages(self):
        while True:
            message = str(input())
            if message == "/getlist":
                client_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                client_socket_udp.sendto('x'.encode(), ("127.0.0.1", 8081))
                data, server_address = client_socket_udp.recvfrom(1024)
                print(data.decode())
                # self.cl_socket.send(message.encode())
            else:
                self.cl_socket.send(message.encode())
            print("sent message to the server")

    def __hash__(self):
        return hash((self.username, self.cl_socket))

    def __eq__(self, other):
        if isinstance(other, Client):
            return self.cl_socket == other.cl_socket and self.username == other.username
        return False


if __name__ == '__main__':
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 8080))
    username = input("Enter your username: ")
    client = Client(client_socket, username)
    client.start()
