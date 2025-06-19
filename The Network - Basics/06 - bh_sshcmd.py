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
            ssh_session.exec_command(command)
            output = ssh_command.recv(1024).decode('utf-8')
            print(output)
    except Exception as e:
        print(f"[!] SSH Connection failed: {e}")
    finally:
        client.close()

ssh_command('192.168.0.107', "Elliot Alderson", 'your_password_here', 'id')

