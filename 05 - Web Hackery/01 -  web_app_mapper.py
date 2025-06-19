import os
import queue
import threading
from urllib import request, error

threads = 10
target = "http://www.blackhatpython.com"
directory = "/Users/justin/Downloads/joomla-3.1.1"
filters = [".jpg", ".gif", ".png", ".css"]

# Change current working directory to the scan root
os.chdir(directory)

# Use thread-safe queue
web_paths = queue.Queue()

# Walk through all files and add eligible ones to the queue
for r, d, f in os.walk("."):
    for file in f:
        remote_path = os.path.join(r, file)
        if remote_path.startswith("."):
            remote_path = remote_path[1:]
        if os.path.splitext(file)[1] not in filters:
            web_paths.put(remote_path.replace("\\", "/"))  # Normalize slashes for URLs

# Function to be run by each thread
def test_remote():
    while not web_paths.empty():
        path = web_paths.get()
        url = f"{target}{path}"

        try:
            req = request.Request(url)
            with request.urlopen(req) as response:
                content = response.read()
                print(f"[{response.status}] => {path}")
        except error.HTTPError as e:
            # Uncomment below line to debug failed codes
            # print(f"Failed {e.code} => {path}")
            pass
        except error.URLError as e:
            print(f"[!] Connection failed: {e.reason}")

# Launch threads
for i in range(threads):
    print(f"[*] Spawning thread: {i}")
    t = threading.Thread(target=test_remote)
    t.start()
