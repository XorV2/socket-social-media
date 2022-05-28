import socket


s = socket.socket()
s.connect(("192.168.0.14", 8000))
while True:
    data = s.recv(1024).decode()
    if data is None:
        break
    s.sendall(input(data).encode())
