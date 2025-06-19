import ctypes
import random
import time
import sys

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

keystrokes = 0
mouse_clicks = 0
double_clicks = 0

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("dwTime", ctypes.c_ulong)
    ]

def get_last_input():
    """Returns the milliseconds since last user input."""
    struct_lastinputinfo = LASTINPUTINFO()
    struct_lastinputinfo.cbSize = ctypes.sizeof(LASTINPUTINFO)

    user32.GetLastInputInfo(ctypes.byref(struct_lastinputinfo))
    run_time = kernel32.GetTickCount()
    elapsed = run_time - struct_lastinputinfo.dwTime

    print(f"[*] It's been {elapsed} milliseconds since the last input event.")
    return elapsed

def get_key_press():
    """Detects a key press or mouse click and returns the timestamp."""
    global mouse_clicks, keystrokes

    for i in range(0, 0xFF):
        state = user32.GetAsyncKeyState(i)

        if state & 0x0001:  # Key was pressed
            if i == 0x01:  # Left mouse click
                mouse_clicks += 1
                return time.time()

            elif 0x30 <= i <= 0x5A:  # Alphanumeric keys
                keystrokes += 1
                return time.time()

    return None

def detect_sandbox():
    global double_clicks

    max_keystrokes = random.randint(10, 25)
    max_mouse_clicks = random.randint(5, 25)
    max_double_clicks = 10
    double_click_threshold = 0.250  # seconds
    max_input_threshold = 30000  # milliseconds

    double_clicks = 0
    first_double_click = None
    previous_timestamp = None

    print("[*] Starting sandbox detection...")
    last_input = get_last_input()
    if last_input >= max_input_threshold:
        print("[!] No user activity detected. Exiting.")
        sys.exit(0)

    while True:
        timestamp = get_key_press()

        if timestamp is not None and previous_timestamp is not None:
            elapsed = timestamp - previous_timestamp

            if elapsed <= double_click_threshold:
                double_clicks += 1
                if first_double_click is None:
                    first_double_click = time.time()
                elif double_clicks == max_double_clicks:
                    total_double_click_time = time.time() - first_double_click
                    if total_double_click_time <= (max_double_clicks * double_click_threshold):
                        print("[!] Sandbox behavior detected. Exiting.")
                        sys.exit(0)

        if (
            keystrokes >= max_keystrokes and
            mouse_clicks >= max_mouse_clicks and
            double_clicks >= max_double_clicks
        ):
            print("[*] User interaction verified. Exiting detection.")
            return

        previous_timestamp = timestamp if timestamp is not None else previous_timestamp

# Run the detection
detect_sandbox()
print("[*] Sandbox check passed. Continuing execution...")
