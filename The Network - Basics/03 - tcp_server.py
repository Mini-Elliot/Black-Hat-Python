import socket
import threading

# ------------------------
# Server Configuration
# ------------------------

BIND_IP = "0.0.0.0"       # Listen on all interfaces
BIND_PORT = 9999          # Port to bind the server

# ------------------------
# Start TCP Server
# ------------------------

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((BIND_IP, BIND_PORT))
server.listen(5)  # Max queued connections

print(f"[*] Listening on {BIND_IP}:{BIND_PORT}")


# ------------------------
# Handle Client Connection
# ------------------------

def handle_client(client_socket, address):
    """
    Handles incoming client connection in a separate thread.
    Continuously receives data and sends back an acknowledgment.
    """
    print(f"[*] New connection from {address[0]}:{address[1]}")
    try:
        while True:
            request = client_socket.recv(1024)
            if not request:
                print(f"[*] Client {address[0]}:{address[1]} disconnected.")
                break

            print(f"[*] Received from {address[0]}:{address[1]}: {request.decode().strip()}")
            client_socket.send(b"ACK!")  # Simple response

    except Exception as e:
        print(f"[!] Error handling client {address[0]}:{address[1]}: {e}")
    
    finally:
        client_socket.close()


# ------------------------
# Main Server Loop
# ------------------------

def start_server():
    """
    Main loop that accepts incoming connections and spawns a thread
    for each client.
    """
    while True:
        client_socket, client_address = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()


if __name__ == "__main__":
    start_server()
