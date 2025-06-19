import sys
import socket
import argparse
import threading
import subprocess


# Parse command-line arguments
def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target", help="Target IP address")
    parser.add_argument("-p", "--port", dest="port", type=int, help="Target port")
    parser.add_argument("-l", "--listen", dest="listen", action="store_true", help="Listen for incoming connections")
    parser.add_argument("-e", "--execute", dest="execute", help="Execute specified file upon receiving a connection")
    parser.add_argument("-c", "--command", dest="command", action="store_true", help="Initialize a command shell")
    parser.add_argument("-u", "--upload", dest="upload_destination", help="Upon receiving connection, upload a file and write to destination")

    args = parser.parse_args()

    # Basic validation
    if not args.listen and (not args.target or not args.port):
        parser.error("[-] You must specify a target and port when not listening.")
    
    return args


args = get_arguments()


# Sends data to the target from stdin and receives response
def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((args.target, args.port))

        if buffer:
            client.send(buffer.encode())

        while True:
            # Wait for response
            response = b""
            while True:
                data = client.recv(4096)
                response += data
                if len(data) < 4096:
                    break
            print(response.decode(), end="")

            # Wait for more input
            buffer = input("") + "\n"
            client.send(buffer.encode())

    except Exception as e:
        print(f"[*] Exception! Exiting. Reason: {e}")
        client.close()


# Executes a shell command and returns output
def run_command(command):
    command = command.strip()
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except Exception as e:
        output = f"Failed to execute command.\n{e}".encode()
    return output


# Handles the incoming client request on the server
def client_handler(client_socket):
    # Handle file upload if specified
    if args.upload_destination:
        file_buffer = b""

        # Read incoming data
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            file_buffer += data

        try:
            with open(args.upload_destination, "wb") as f:
                f.write(file_buffer)
            client_socket.send(f"Successfully saved file to {args.upload_destination}\n".encode())
        except Exception as e:
            client_socket.send(f"Failed to save file. Error: {e}\n".encode())

    # Handle command execution
    if args.execute:
        output = run_command(args.execute)
        client_socket.send(output)

    # Command shell
    if args.command:
        while True:
            try:
                client_socket.send(b"<BHP:#> ")
                cmd_buffer = ""
                while "\n" not in cmd_buffer:
                    cmd_buffer += client_socket.recv(1024).decode()
                response = run_command(cmd_buffer)
                client_socket.send(response)
            except Exception as e:
                print(f"[*] Command shell error: {e}")
                break


# Server-side listener
def server_loop():
    target = args.target if args.target else "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, args.port))
    server.listen(5)

    print(f"[*] Listening on {target}:{args.port}...")

    while True:
        client_socket, addr = server.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


# Main function — entry point
def main():
    if args.listen:
        server_loop()
    else:
        buffer = sys.stdin.read()
        client_sender(buffer)


if __name__ == "__main__":
    main()
