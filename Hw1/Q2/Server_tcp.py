from socket import *
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
        if t[1] == least and t[0] != ' ' and maximum < dm[t[0]]:
            maximum = dm[t[0]]
    return ''.join(list(map(lambda s: str(dm[s]) if s != ' ' else ' ', client_data))) + " , " + str(maximum)


server_port = 12000
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(("", server_port))
server_socket.listen(1)
print("TCP Server Started")
while True:
    connection_socket, addr = server_socket.accept()
    message = connection_socket.recv(1024).decode()
    if message == 'exit':
        print(f"tcp client with address {addr} disconnected")

    tcp_response = transform_tcp(message)
    connection_socket.send(tcp_response.encode())
