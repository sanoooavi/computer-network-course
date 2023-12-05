from socket import *
import threading
from collections import Counter


def transform_tcp(client_data):
    dm = {'a': 0, 'b': 0,
          'c': 1, 'd': 1,
          'e': 2, 'f': 2,
          'g': 3, 'h': 3,
          'i': 4, 'j': 4,
          'k': 5, 'l': 5,
          'm': 6, 'n': 6,
          'o': 7, 'p': 7,
          'q': 8, 'r': 8,
          's': 9, 't': 9,
          'u': 10, 'v': 10,
          'w': 11, 'x': 11,
          'y': 12, 'z': 12
          }
    ctr = Counter(client_data)
    least = ctr.most_common()[-1][1]
    maximum = -1
    for t in ctr.most_common():
        if t[1] == least and t[0] in dm.keys() and maximum < dm[t[0]]:
            maximum = dm[t[0]]
    return ''.join(list(map(lambda s: str(dm[s]) if s in dm.keys() else s, client_data))) + " , " + str(maximum)


def transform_udp(client_data):
    counted = Counter(client_data)
    return client_data.upper()[::-1] + " , " + counted.most_common()[0][0].upper()


def tcp_client_thread(tcp_socket, address):
    while True:
        data = tcp_socket.recv(1024)
        if not data:
            break
        msg = data.decode()
        if msg == 'exit':
            print(f"tcp client with address {address} disconnected")
            break
        msg = transform_tcp(msg)
        tcp_socket.send(msg.encode())


server_port = 12000
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(("", server_port))
server_socket.listen(5)
print("TCP Server Started")
while True:
    connection_socket, addr = server_socket.accept()
    client_thread = threading.Thread(target=tcp_client_thread, args=(connection_socket, addr))
    client_thread.start()
