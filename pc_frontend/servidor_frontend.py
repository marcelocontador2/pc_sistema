import http.server
import socketserver
import urllib.request
import urllib.error

PORT = 3000
API_BASE = "http://localhost:8000"

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Se for requisição para a API, redireciona
        if self.path.startswith("/analise") or self.path.startswith("/upload") or self.path.startswith("/gerar-pptx"):
            try:
                url = API_BASE + self.path
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req) as response:
                    self.send_response(response.status)
                    for header, value in response.headers.items():
                        if header.lower() not in ["content-length", "transfer-encoding"]:
                            self.send_header(header, value)
                    self.end_headers()
                    self.wfile.write(response.read())
            except urllib.error.URLError as e:
                self.send_error(502, f"Erro no proxy: {e.reason}")
        else:
            # Serve arquivos estáticos (index.html, etc.)
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/upload") or self.path.startswith("/gerar-pptx"):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                url = API_BASE + self.path
                req = urllib.request.Request(url, data=post_data, method='POST')
                req.add_header('Content-Type', self.headers.get('Content-Type'))
                with urllib.request.urlopen(req) as response:
                    self.send_response(response.status)
                    for header, value in response.headers.items():
                        if header.lower() not in ["content-length", "transfer-encoding"]:
                            self.send_header(header, value)
                    self.end_headers()
                    self.wfile.write(response.read())
            except urllib.error.URLError as e:
                self.send_error(502, f"Erro no proxy: {e.reason}")
        else:
            super().do_POST()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
        print(f"Servidor do frontend (com proxy para API) rodando em http://localhost:{PORT}")
        httpd.serve_forever()