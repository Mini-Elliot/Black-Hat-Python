import socket
import threading
import paramiko
import argparse


# Load the RSA key used by the server (generate one if you don't have it)
host_key = paramiko.RSAKey(filename='test_rsa.key')


class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if username == "Elliot Alderson" and password == "your_password_here":
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED


def run_ssh_server(server_ip, ssh_port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server_ip, ssh_port))
        sock.listen(100)
        print(f"[+] Listening for connections on {server_ip}:{ssh_port} ...")
        client, addr = sock.accept()
    except Exception as e:
        print(f"[-] Listen failed: {e}")
        return

    print(f"[+] Got a connection from {addr[0]}:{addr[1]}")

    try:
        bh_session = paramiko.Transport(client)
        bh_session.add_server_key(host_key)
        server = Server()

        try:
            bh_session.start_server(server=server)
        except paramiko.SSHException:
            print("[-] SSH negotiation failed.")
            return

        chan = bh_session.accept(20)
        if chan is None:
            print("[-] No channel received.")
            return

        print("[+] Authenticated!")
        print(chan.recv(1024).decode('utf-8'))
        chan.send("Welcome to bh_ssh\n")

        while True:
            try:
                command = input("Enter command: ").strip()
                if command:
                    chan.send(command)
                    if command.lower() == "exit":
                        print("[*] Exiting session.")
                        bh_session.close()
                        break

                    response = chan.recv(4096)
                    print(response.decode('utf-8'))
            except KeyboardInterrupt:
                print("\n[*] Keyboard interrupt. Closing session.")
                bh_session.close()
                break
    except Exception as e:
        print(f"[-] Caught exception: {e}")
        try:
            bh_session.close()
        except:
            pass


def main():
    parser = argparse.ArgumentParser(description="SSH Command Server using Paramiko")
    parser.add_argument("-i", "--ip", dest="ip", required=True, help="IP address to bind the SSH server to")
    parser.add_argument("-p", "--port", dest="port", required=True, type=int, help="Port to listen on")

    args = parser.parse_args()

    run_ssh_server(args.ip, args.port)


if __name__ == '__main__':
    main()
