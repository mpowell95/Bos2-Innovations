import http.server, socketserver, sys
CSP = ("default-src 'self' https://unpkg.com https://cdn.jsdelivr.net https://esm.sh; "
       "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com "
       "https://cdn.jsdelivr.net https://esm.sh blob:; "
       "style-src 'self' 'unsafe-inline'; connect-src https: data:; form-action 'none'")
class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Content-Security-Policy', CSP)
        super().end_headers()
    def log_message(self,*a): pass
socketserver.TCPServer.allow_reuse_address=True
socketserver.TCPServer(("127.0.0.1",8899),H).serve_forever()
