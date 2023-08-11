import socket
import sys

server = None
client = None

def main():
    global server, client
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 8080))
    server.listen(1)
    client, address = server.accept()
    while True:
        data = client.recv(1024)
        if not data:
            break
        client.sendall(data)
    client.close()
    server.close()

if __name__ == '__main__':
    main()
