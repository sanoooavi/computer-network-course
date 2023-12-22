import socket
import threading
import time

from client import Client

all_clients = []
client_history = {}


class Server_tcp:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"TCP server started on {self.host}:{self.port}")

        while True:
            client_socket, address = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, address)).start()

    def handle_client(self, client_socket, address):
        username = client_socket.recv(1024).decode()
        hashed_password = client_socket.recv(1024).decode()

        if self.is_username_taken(username):
            client_socket.send("Username already taken. Please choose a different username.".encode())
            client_socket.close()
            print(f"Connection from {address} rejected - Username already taken: {username}")
            return

        new_client = Client(client_socket, username, hashed_password)
        all_clients.append(new_client)
        print(f"New connection from {address}, username: {username}, password: {hashed_password}")

        if username in client_history:
            previous_messages = client_history[username]
            for timestamp, message in previous_messages:
                client_socket.send(f"{timestamp} - {message}".encode())

        while True:
            try:
                data = client_socket.recv(1024)
                if str(data.decode()).startswith('/exit'):
                    print(data)
                    break
                message = data.decode()
                self.handle_message(new_client, message)
            except Exception as e:
                print(e)
                break

        all_clients.remove(new_client)
        client_socket.close()
        print(f"Connection with {address}, username: {username} closed")

    def handle_message(self, sender, message):
        if message.startswith("/join"):
            group_name = message.split()[1]
            self.join_group(sender, group_name)

        elif message.startswith("/private"):
            try:
                recipient_username, content = message.split(maxsplit=2)[1:]
            except ValueError:
                sender.cl_socket.send("Not correct message format".encode())
                return
            recipient = self.get_client_by_username(recipient_username)
            if recipient:
                if recipient.status == 'Busy':
                    sender.cl_socket.send(f"{recipient_username} is busy and cannot receive messages.".encode())
                else:
                    self.send_private_message(sender.username, content, recipient)
            else:
                sender.cl_socket.send("Recipient not found".encode())

        elif message.startswith("/public"):
            try:
                group_id, content = message.split(maxsplit=2)[1:]
            except ValueError:
                sender.cl_socket.send("Not correct message format".encode())
                return
            self.send_group_message(sender, group_id, content)

        elif message.startswith("/getlist"):
            username_list = '-'.join([obj.username for obj in all_clients])
            sender.cl_socket.send(username_list.encode())

        elif message.startswith('/getMessages'):
            previous_messages = client_history[sender.username]
            for timestamp, message in previous_messages:
                sender.cl_socket.send(f"{timestamp} - {message}".encode())

        else:
            sender.cl_socket.send("Invalid command".encode())

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.add_message_to_history(sender.username, timestamp, message)

    def join_group(self, client, group_name):
        if group_name in client.group_chats:
            client.cl_socket.send("You are already in this group".encode())
        else:
            client.group_chats.append(group_name)
            client.cl_socket.send(f"You joined the group: {group_name}".encode())

    def send_private_message(self, sender_username, content, recipient):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        recipient.cl_socket.send(f"{timestamp} - {sender_username}: {content}".encode())

    def send_group_message(self, sender, group_id, content):
        if group_id in sender.group_chats:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            for cl in all_clients:
                if cl.status == 'Available' and group_id in cl.group_chats:
                    cl.cl_socket.send(f"{timestamp} - {sender.username}: {content} in {group_id}".encode())
        else:
            sender.cl_socket.send("You are not in this group".encode())

    def get_client_by_username(self, username):
        for client in all_clients:
            if client.username == username:
                return client
        return None

    def is_username_taken(self, username):
        for client in all_clients:
            if client.username == username:
                return True
        return False

    def add_message_to_history(self, username, timestamp, message):
        if username in client_history:
            client_history[username].append((timestamp, message))
        else:
            client_history[username] = [(timestamp, message)]


class Server_udp:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        print(f"UDP server started on {self.host}:{self.port}")
        while True:
            data, client_address = self.server_socket.recvfrom(1024)
            username_list = '-'.join([obj.username for obj in all_clients])
            print(client_address)
            # timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # self.add_message_to_history(sender.username, timestamp, message)
            self.server_socket.sendto(username_list.encode(), client_address)


if __name__ == "__main__":
    tcp_server = Server_tcp('localhost', 5000)
    udp_server = Server_udp('localhost', 5001)

    tcp_thread = threading.Thread(target=tcp_server.start)
    udp_thread = threading.Thread(target=udp_server.start)

    tcp_thread.start()
    udp_thread.start()
