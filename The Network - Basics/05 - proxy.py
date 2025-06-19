import sys
import socket
import threading
import argparse

class TCP_Proxy():
    def __init__(self):
        pass

    def get_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-lh", "--local-host", dest="local_host", help="Local IP address to bind to")
        parser.add_argument("-lp", "--local-port", dest="local_port", type=int, help="Local port to bind to ")
        parser.add_argument("-rh", "--remote-host", dest="remote_host", help="Remote target IP address")
        parser.add_argument("-rp", "--remote-port", dest="remote_port", type=int, help="Remote target port")
        parser.add_argument("-rf", "--receive-first", dest="receive_first", action="store_true", help="Receive data from remote before sending it")
        args = parser.parse_args()
        if not args.local_host:
            parser.error("Please Specify an IP address for localhost")
        elif not args.local_port:
            parser.error("Please specify a port of localhost")
        elif not args.remote_host:
            parser.error("Please Specify a remote target IP address")
        elif not args.remote_port:
            parser.error("Please specify a remote target port")
        return args

    def server_loop(self, local_host, local_port, remort_host, remort_port, receive_first):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            server.bind((local_host, local_port))
        except Exception as e:
            print(f"[-] Failed to bind on {local_host}:{local_port}: {e}")
            sys.exit(1)

        print(f"[*] listening on {local_host}:{local_port}")
        server.listen(5)
        
        while True:
            client_socket, address = server.accept()

            #print the local connection information
            print(f"[==>] Received incomming connections from {address[0]}:{address[1]}")

            #start a thread to talk to remote host
            proxy_thread = threading.Thread(target=self.proxy_handler, args=(client_socket, remort_host, remort_port, receive_first),)
            proxy_thread.start()

    def hexdump(self, src, length=16):

        results = []
        for i in range(0, len(src), length):
            s = src[i:i+length]
            hexa = ' '.join(f"{b:02X}" for b in s)
            text = ''.join(chr(b) if 0x20 <= b < 0x7F else '.' for b in s)
            results.append(f"{i:04X} {hexa:<{length*3}} {text}")
        
        print('\n'.join(results))

    def receive_from(self, connection):
        buffer = b""
        # We set a 2 second timeout; depending on your target, this may need to be adjusted
        connection.settimeout(2)

        try:
            # Keep reading into data until there is no more data or we timeout
            while True:
                data = connection.recv(4096)
                if not data:
                    break
                buffer += data
        except:
            pass
        return buffer

    def request_handler(self, buffer):
        #perform packet modification
        return buffer

    def response_handler(self, buffer):
        #perform packet modification
        return buffer

    def proxy_handler(self, client_socket, remote_host, remote_port, receive_first):
        #connect to remote host
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((remote_host, remote_port))

        #receive data from remote end if necessary
        if receive_first:
            remote_buffer = self.receive_from(remote_socket)
            if remote_buffer:
                print(f"[<==] Received {len(remote_buffer)} bytes from remote")
                self.hexdump(remote_buffer)
                #send it to our response handler
                remote_buffer = self.response_handler(remote_buffer)
                client_socket.send(remote_buffer)

        #now let's loop and read from local, send to remote, send to local. Rinse, watch, repeat
        while True:
            #read from local host
            local_buffer = self.receive_from(client_socket)

            if local_buffer:
                print(f"[<==] Received {len(local_buffer)} bytes from localhost.")
                self.hexdump(local_buffer)

                #send it to our request handler
                local_buffer = self.request_handler(local_buffer)

                #send of the data to remote host
                remote_socket.send(local_buffer)
                print("[==>] Sent to remote.")

            #receive back the response
            remote_buffer = self.receive_from(remote_socket)
            if remote_buffer:
                print(f"[<==] Received {len(remote_buffer)} bytes from remote.")
                self.hexdump(remote_buffer)
                remote_buffer = self.response_handler(remote_buffer)
                client_socket.send(remote_buffer)
                print("[==>] Sent to localhost.")

            if not local_buffer or not remote_buffer:
                client_socket.close()
                remote_socket.close()
                print("[*] No more data. Closing Connections.")
                break

    def main(self):
        options = self.get_arguments()
        self.server_loop(options.local_host, options.local_port, options.remote_host, options.remote_port, options.receive_first)

if __name__ == "__main__":
    proxy = TCP_Proxy()
    proxy.main()
    

