import socket

target_host = "example.com"
target_port = 80

#create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#create a client
client.connect((target_host, target_port))

#send some data
client.send(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")

#recive some data
response = client.recv(4096)

print(response.decode())