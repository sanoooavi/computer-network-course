import os
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
        if os.path.exists("D:\\uni\\sem7\\network\\computer-network-course\\Hw2\\Q1\\client_history.txt"):
            self.load_client_history()
        if os.path.exists("D:\\uni\\sem7\\network\\computer-network-course\\Hw2\\Q1\\client_list.txt"):
            self.load_clients_from_file()
        print(f"TCP server started on {self.host}:{self.port}")

        while True:
            client_socket, address = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, address)).start()

    def handle_client(self, client_socket, address):
        username = client_socket.recv(1024).decode()
        hashed_password = client_socket.recv(1024).decode()

        new_client = self.get_client_by_username(username)

        if new_client is not None and new_client.username == username:
            print('ta inja kar mikone 1')
            if new_client.password == hashed_password:
                new_client.cl_socket = client_socket
                client_socket.send('welcome back'.encode())
                if username in client_history:
                    previous_messages = client_history[username]
                    for timestamp, message in previous_messages:
                        client_socket.send(f"{timestamp} - {message}".encode())
            else:
                client_socket.send("Username already taken. Please choose a different username.".encode())
                client_socket.close()
                print(f"Connection from {address} rejected - Username already taken: {username}")
                return
        else:
            new_client = Client(client_socket, username, hashed_password)
            all_clients.append(new_client)
            self.add_client_to_file(new_client)
        print(f"New connection from {address}, username: {username}, password: {hashed_password}")
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

    def add_client_to_file(self, client):
        with open('client_list.txt', 'a') as file:
            file.write(f"Username: {client.username}, Password: {client.password}\n")

    def load_clients_from_file(self):
        with open('client_list.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith('Username:'):
                    username = line.split(',')[0].split(':')[1].strip()
                    password = line.split(',')[1].split(':')[1].strip()
                    new_client = Client(None, username, password)
                    all_clients.append(new_client)

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
        return

    def send_private_message(self, sender_username, content, recipient):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        recipient.cl_socket.send(f"{timestamp} - {sender_username}: {content}".encode())

    def send_group_message(self, sender, group_id, content):
        print('ta inja reside')
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
                return client
        return None

    def add_message_to_history(self, username, timestamp, message):
        if username in client_history:
            client_history[username].append((timestamp, message))
        else:
            client_history[username] = [(timestamp, message)]

    def save_client_history(self):
        with open('client_history.txt', 'w') as file:
            for username, messages in client_history.items():
                file.write(f"Username: {username}\n")
                for timestamp, message in messages:
                    file.write(f"{timestamp} - {message}\n")

    def load_client_history(self):
        try:
            with open('client_history.txt', 'r') as file:
                lines = file.readlines()
                username = ''
                for line in lines:
                    if line.startswith('Username:'):
                        username = line.split(':')[1].strip()
                        client_history[username] = []
                    else:
                        timestamp, message = line.strip().split(' - ', 1)
                        client_history[username].append((timestamp, message))
        except FileNotFoundError:
            print("No client history file found.")

    def shutdown(self):
        self.save_client_history()
        self.server_socket.close()


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
            # print(client_address)
            # timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # self.add_message_to_history(sender.username, timestamp, message)
            self.server_socket.sendto(username_list.encode(), client_address)

    def shutdown(self):
        self.server_socket.close()


if __name__ == "__main__":
    tcp_server = Server_tcp('localhost', 5000)
    udp_server = Server_udp('localhost', 5001)

    tcp_thread = threading.Thread(target=tcp_server.start)
    udp_thread = threading.Thread(target=udp_server.start)
    tcp_thread.start()
    udp_thread.start()
    try:
        while True:
            inp = input()
            if inp == 'exit':
                print(inp)
                tcp_server.shutdown()
                # udp_server.shutdown()
                exit(1)
                print("After exit")  # This line will not be executed
            time.sleep(1)
    except KeyboardInterrupt:
        tcp_server.shutdown()
        udp_server.shutdown()
        exit()
