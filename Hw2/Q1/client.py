import hashlib
import socket
import threading


class Client:
    def __init__(self, cl_socket, username, password):
        self.cl_socket = cl_socket
        self.status = 'Busy'
        self.username = username
        self.password = password
        self.group_chats = []

    def start(self):
        threading.Thread(target=self.send_messages).start()
        threading.Thread(target=self.receive_messages).start()

    def receive_messages(self):
        while True:
            try:
                message = self.cl_socket.recv(1024).decode()
                if not message:
                    self.cl_socket.close()
                    break
                print(message)
            except:
                self.cl_socket.close()
                break

    def send_messages(self):
        while True:
            message = str(input())
            if message == '/status':
                self.cl_socket.send(message.encode())
                self.set_status('Available' if self.status == 'Busy' else 'Busy')
                print("Your new status is:", self.status)
                continue
            if self.status == 'Busy':
                print("You are currently in Busy mode and cannot send messages.")
            else:
                if message == "/getlist":
                    client_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    client_socket_udp.sendto('x'.encode(), ("127.0.0.1", 5001))
                    data, server_address = client_socket_udp.recvfrom(1024)
                    print(data.decode())
                else:
                    self.cl_socket.send(message.encode())
                print("Sent message to the server")

    def set_status(self, new_status):
        self.status = new_status

    def __hash__(self):
        return hash((self.username, self.cl_socket))

    def __eq__(self, other):
        if isinstance(other, Client):
            return self.cl_socket == other.cl_socket and self.username == other.username
        return False


if __name__ == '__main__':
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 5000))
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    client_socket.send(username.encode())
    client_socket.send(hashed_password.encode())

    client = Client(client_socket, username, hashed_password)
    client.start()
