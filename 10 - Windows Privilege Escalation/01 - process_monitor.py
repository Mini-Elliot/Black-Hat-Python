import win32con
import win32api
import win32security
import wmi
import sys
import os
import datetime

LOG_FILE = "process_monitor_log.csv"

def log_to_file(message):
    with open(LOG_FILE, "a", encoding="utf-8") as fd:
        fd.write(f"{message}\r\n")

# Create header if not already present
if not os.path.isfile(LOG_FILE):
    log_to_file("Time,User,Executable,CommandLine,PID,Parent PID,Privileges")

# WMI interface
c = wmi.WMI()
process_watcher = c.Win32_Process.watch_for("creation")

def get_process_privileges(pid):
    try:
        # Obtain a handle to the target process
        hproc = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
        # Open the main process token
        htok = win32security.OpenProcessToken(hproc, win32con.TOKEN_QUERY)
        # Retrieve the list of privileges
        privs = win32security.GetTokenInformation(htok, win32security.TokenPrivileges)

        priv_list = ""
        for priv_id, flags in privs:
            # Check if privilege is enabled (flag == 2 or 3)
            if flags & (win32con.SE_PRIVILEGE_ENABLED | win32con.SE_PRIVILEGE_ENABLED_BY_DEFAULT):
                priv_name = win32security.LookupPrivilegeName(None, priv_id)
                priv_list += f"{priv_name}|"

        return priv_list if priv_list else "None"
    except Exception:
        return "N/A"

# Main monitor loop
while True:
    try:
        new_process = process_watcher()
        proc_owner = new_process.GetOwner()
        owner_str = f"{proc_owner[0]}\\{proc_owner[2]}"

        create_time = datetime.datetime.strptime(str(new_process.CreationDate[:14]), "%Y%m%d%H%M%S")
        timestamp = create_time.strftime("%Y-%m-%d %H:%M:%S")

        executable = new_process.ExecutablePath or "N/A"
        cmdline = new_process.CommandLine or "N/A"
        pid = new_process.ProcessId
        parent_pid = new_process.ParentProcessId
        privileges = get_process_privileges(pid)

        log_entry = f"{timestamp},{owner_str},{executable},{cmdline},{pid},{parent_pid},{privileges}"
        print(log_entry)
        log_to_file(log_entry)

    except KeyboardInterrupt:
        print("\n[+] Exiting process monitor.")
        sys.exit(0)
    except Exception:
        pass
