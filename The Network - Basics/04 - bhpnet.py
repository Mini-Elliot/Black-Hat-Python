import sys
import socket
import getopt
import threading
import subprocess
import argparse


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target", help="Specify the IP address of target")
    parser.add_argument("-p", "--port", dest="port", type=int, help="Specify the port for connection")
    parser.add_argument("-l", "--listen", dest="listen", action="store_true", default=False, help="listen on [host]:[port] for incoming connections")
    parser.add_argument("-e", "--execute", dest="execute", help="execute the give file upon receiving a connection")
    parser.add_argument("-c", "--command", dest="command", action="store_true", default=False, help="initialize a shell command")
    parser.add_argument("-u", "--upload", dest="upload_destination", help="upon receiving connection upload a file and write to [destination]\n\n")
    args = parser.parse_args()

    if not args.target:
        parser.error(f"[-] Please specify an IP address for target.")
    elif not args.port:
        parser.error(f"[-] Please specify a port for connection.")
    return args

args = get_arguments()


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((args.target, args.port))
        if len(buffer):
            client.send(buffer.encode())
            while True:
                # Now wait for data back
                recv_len = 1
                response = b""
                while recv_len:
                    data = client.recv(4096)
                    recv_len = len(data)
                    response += data
                    if recv_len < 4096:
                        break
                print(response)
                # wait for more info
                buffer = input("") + "\n"
                #send it off
                client.send(buffer.encode())
    except Exception as e:
        print(f"[*] Exception! Exiting. Reason: {e}")
        # tear down the connection
        client.close()

def client_handler(client_socket):
    # check for uploads
    if len(args.upload_destination):
        #read all the bytes and return to the destination
        file_buffer = b""   
        #keep reading data until none is available
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else: 
                file_buffer += data  
        # Now we take these bytes and try to write them
        try:
            with open(args.upload_destination, "wb") as file_discriptor:
                file_discriptor.write(file_buffer)
                file_discriptor.close()
        except:
            client_socket.send(f"Failed to save file {args.upload_destination}".encode()) 
    #check for command execution
    if len(args.execute):
        #run the command
        output = run_command(args.execute)
        client_socket.send(output)
    #now we go to another loop if the command shell is requested
    if args.command:
        while True:
            #show a simple prompt
            client_socket.send(b"<BHP:#> ")

            #now we receive until we see a line feed (enter key)
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode()

            #send back the response output
            response = run_command(cmd_buffer)

            #send back the response
            client_socket.send(response)


def run_command(command):
    # trim the new line
    command = command.strip()
    # run the command and get the output
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command \r\n"
    # send the output back to client
    return output


def server_loop():
    # if no target is defined, we listen on all interface
    if not len(args.target):
        target = "0.0.0.0."
        
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((args.target, args.port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        #spin of a thread to handle our new client
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def main():
    #are we going to listen or just send data from stdin?
    if not args.listen and len(args.target) and args.port > 0:
        #read in the buffer from the commandline
        # this will block, so send CTRL-D if not sending input
        # to stdin
        buffer = sys.stdin.read()

        #send data off
        client_sender(buffer)

        # we are going to listen and potentially
        # upload things, execute commands, drop a shell back
        # depending on our command line options above
        if args.listen:
            server_loop()

if __name__ == "__main__":
    main()