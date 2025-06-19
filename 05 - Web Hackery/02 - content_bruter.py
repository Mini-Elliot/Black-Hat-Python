import threading
import queue
import urllib.request
import urllib.error
import urllib.parse
import os

# === Configuration ===
threads = 50
target_url = "http://testphp.vulnweb.com"
wordlist_file = "/tmp/all.txt"  # Make sure this file exists
resume = None  # Set to a string if you want to resume
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"
extensions = [".php", ".bak", ".orig", ".inc"]


# === Wordlist Builder ===
def build_wordlist(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        raw_words = f.read().splitlines()

    word_queue = queue.Queue()
    found_resume = resume is None

    for word in raw_words:
        word = word.strip()
        if not word:
            continue

        if found_resume:
            word_queue.put(word)
        elif word == resume:
            found_resume = True
            print(f"[*] Resuming wordlist from: {resume}")
            word_queue.put(word)

    return word_queue


# === Directory Brute Forcing Thread ===
def dir_bruter(word_queue, extensions=None):
    while not word_queue.empty():
        attempt = word_queue.get()
        attempt_list = []

        # Directory vs file
        if '.' not in attempt:
            attempt_list.append(f"/{attempt}/")
        else:
            attempt_list.append(f"/{attempt}")

        # Try extensions
        if extensions:
            for ext in extensions:
                attempt_list.append(f"/{attempt}{ext}")

        # Test each path
        for brute_path in attempt_list:
            url = f"{target_url}{urllib.parse.quote(brute_path)}"
            headers = {'User-Agent': user_agent}
            req = urllib.request.Request(url, headers=headers)

            try:
                with urllib.request.urlopen(req) as response:
                    content = response.read()
                    if content:
                        print(f"[{response.status}] => {url}")
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    print(f"[!!! {e.code}] => {url}")
            except urllib.error.URLError as e:
                print(f"[!] Failed to connect to {url}: {e.reason}")
            except Exception as e:
                print(f"[!] Unexpected error on {url}: {e}")


# === Main Execution ===
if __name__ == "__main__":
    if not os.path.exists(wordlist_file):
        print(f"[!] Wordlist file not found: {wordlist_file}")
        exit(1)

    print("[*] Building wordlist...")
    word_queue = build_wordlist(wordlist_file)
    print(f"[*] Wordlist loaded: {word_queue.qsize()} entries")

    for i in range(threads):
        t = threading.Thread(target=dir_bruter, args=(word_queue, extensions))
        t.start()
