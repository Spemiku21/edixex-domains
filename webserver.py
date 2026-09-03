from http.server import HTTPServer, BaseHTTPRequestHandler
from domains import resolve

HOST = "0.0.0.0"
PORT = 8080


class Server(BaseHTTPRequestHandler):

    def do_GET(self):
        # URL'den domaini al
        domain = self.headers.get("Host", "").split(":")[0]

        # Domain sistemimizden IP'yi bul
        ip = resolve(domain)

        if ip:
            message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{domain}</title>
            </head>
            <body>
                <h1>🚀 {domain}</h1>
                <p>Domain başarıyla bulundu!</p>
                <p>Sunucu: {ip}</p>
            </body>
            </html>
            """
        else:
            message = """
            <!DOCTYPE html>
            <html>
            <body>
                <h1>❌ Domain bulunamadı</h1>
            </body>
            </html>
            """

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )
        self.end_headers()

        self.wfile.write(message.encode("utf-8"))


server = HTTPServer((HOST, PORT), Server)

print("🚀 EdixexSMP server çalışıyor!")
print("http://127.0.0.1:8080")

server.serve_forever()