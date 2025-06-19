# 🐍 Black Hat Python Tools – Upgraded to Python 3

This repository is a modernized, Python 3-compatible reimplementation of tools from the legendary book  
**Black Hat Python** by *Justin Seitz*.

> 🧠 All credit for the original ideas and tool designs belongs to the author.  
> I, **[Mini-Elliot](https://github.com/Mini-Elliot)**, have simply upgraded the code to Python 3 and made it more reliable for educational and ethical use.

---

## ⚠️ Legal Disclaimer

This project is intended **only for educational purposes**, network auditing, and **authorized penetration testing**.  
Any misuse of the tools is **strictly the responsibility of the user**.  

> **📛 The developer is not liable** for any criminal or unethical behavior using this code.  
> If you use this in an illegal manner, **you alone are accountable** — not me, the developer.

---

## 🚀 Goals of the Project

- 🔁 Upgrade all Python 2 code to **Python 3**
- 💪 Improve reliability and portability
- 🧼 Clean up syntax and error handling
- 🧪 Enable educational testing in modern systems
- 🛠️ Keep functionality true to the original book

---

## 🧰 Tools Being Upgraded

| Category                     | Examples                                                                 |
| ---------------------------- | ------------------------------------------------------------------------ |
| 🖧 **Networking Tools**      | TCP clients/servers, socket sniffers, proxies, port scanners             |
| 🕵️ **Reconnaissance Tools** | Packet sniffers, ARP spoofers, host discovery, network mappers           |
| 🐍 **Python Automation**     | Burp Proxy plugins, GitHub control, browser scripting                    |
| 🎯 **Post-Exploitation**     | Reverse shells, file upload/download, keyloggers, persistence mechanisms |
| 📡 **Web & SSH Tools**       | Paramiko automation, brute-forcers, web interaction tools                |
| 🧱 **Windows Exploits**      | Privilege escalation, DLL injection, registry backdoors                  |
| 🧪 **Forensic Evasion**      | Memory dumping, timestamp manipulation, log tampering                    |

---

## ✅ Upgrade Progress

| Tool                                                     | Status        |
|----------------------------------------------------------|---------------|
| The Network: Basics                                      | ⏳ In Progress |
| The Network: Raw Sockets and Sniffing                    | ✅ Done        |
| Owning The Network with Scapy                            | ✅ Done        |
| Web Hackery                                              | ✅ Done        |
| Extending Burp Proxy                                     | ❌ Pending     |
| GitHub Command and Control                               | ❌ Pending     |
| Common Trojaning Tasks on Windows                        | ✅ Done        |
| Fun with Internet Explorer                               | ✅ Done        |
| Windows Privilege Escalation                             | ✅ Done        |
| Automating Offensive Forensics                           | ✅ Done        |

---

## 📦 Installation

To run these tools, Python 3 is required. Recommended version: **3.9+**.

### 🔧 Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Mini-Elliot/Black-Hat-Python.git
   cd Black-Hat-Python
   ```
### 🧪 Create a Virtual Environment (Optional)

It's recommended to use a virtual environment to manage dependencies.
2. ** Linux/macOS**
```bash
python -m venv venv
source venv/bin/activate
```
3. **Install All Dependencies**
```bash
pip install -r requirements.txt
```
4. **Install Volatility 3**
```bash
git clone https://github.com/volatilityfoundation/volatility3
cd volatility3
pip install -r requirements.txt
```
