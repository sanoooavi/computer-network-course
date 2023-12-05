import socket
import threading

from client import Client

all_clients = []


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
        # Receive username from client
        username = client_socket.recv(1024).decode()
        new_client = Client(client_socket, username)
        all_clients.append(new_client)
        print(f"New connection from {address}, username: {username}")

        while True:
            try:
                data = client_socket.recv(1024)
                if str(data.decode()).startswith('/exit'):
                    print(data)
                    break
                message = data.decode()
                self.handle_message(new_client, message)
            except:
                break

        all_clients.remove(new_client)
        client_socket.close()
        print(f"Connection with {address}, username: {username} closed")
        print('here1')

    def handle_message(self, sender, message):
        if message.startswith("/join"):
            group_name = message.split()[1]
            self.join_group(sender, group_name)

        elif message.startswith("/private"):
            try:
                recipient_username, content = message.split()[1:]
            except:
                sender.cl_socket.send("Not correct message format".encode())
                return
            recipient = self.get_client_by_username(recipient_username)
            if recipient:
                self.send_private_message(sender.username, content, recipient)
            else:
                sender.cl_socket.send("Recipient not found".encode())

        elif message.startswith("/public"):
            group_id, content = message.split()[1:]
            self.send_group_message(sender, group_id, content)

        elif message.startswith("/getlist"):
            # print('list ro mikhad...')
            username_list = 'no people'
            try:
                username_list = '-'.join([obj.username for obj in all_clients])
            except Exception as e:
                print("An exception occurred:", e)
            sender.cl_socket.send(username_list.encode())
        else:
            sender.cl_socket.send("Invalid command".encode())

    def join_group(self, client, group_name):
        if group_name in client.group_chats:
            client.cl_socket.send("You are already in this group".encode())
        else:
            client.group_chats.append(group_name)
            client.cl_socket.send(f"You joined the group: {group_name}".encode())

    def send_private_message(self, sender_username: str, content: str, recipient):
        recipient.cl_socket.send(f"{sender_username}: {content}".encode())

    def send_group_message(self, sender, group_id: str, content: str):
        if group_id in sender.group_chats:
            for cl in all_clients:
                if group_id in Client(cl).group_chats:
                    Client(cl).cl_socket.send(f"{sender.username}: {content} in {group_id}".encode())
        else:
            sender.cl_socket.send("You are not in this group".encode())

    def get_client_by_username(self, username):
        for client in all_clients:
            if client.username == username:
                return client
        print('not found')
        return None


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
            self.server_socket.sendto(username_list.encode(), client_address)


if __name__ == '__main__':
    tcp_server = Server_tcp('127.0.0.1', 8080)
    udp_server = Server_udp('127.0.0.1', 8081)
    threading.Thread(target=udp_server.start).start()
    threading.Thread(target=tcp_server.start).start()
