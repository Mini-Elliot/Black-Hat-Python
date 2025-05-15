import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))

server.listen(5)

print(f"[*] Listening on {bind_ip}:{bind_port}")

#this is our client handling thread
def handle_client(client_socket):
    while True:
        #print what the client sends
        request = client_socket.recv(1024)
        if not request:
            break
        print(f"[*] Received: {request.decode()}")
        #send back a packet
        client_socket.send(b"ACK!")
    client_socket.close()

while True:
    client, addr = server.accept()
    
    print(f"[*] Accept Connection from: {addr[0]}:{addr[1]}")
    #spin our client thread to handle incoming data
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()