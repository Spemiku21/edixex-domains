from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from domains import domains, add_domain, remove_domain

HOST = "0.0.0.0"
PORT = 8081


class Panel(BaseHTTPRequestHandler):

    def do_GET(self):
        url = urlparse(self.path)

        if url.path == "/":
            self.home()

        elif url.path == "/add":
            data = parse_qs(url.query)

            domain = data.get("domain", [""])[0]
            ip = data.get("ip", [""])[0]

            if domain and ip:
                add_domain(domain, ip)

            self.redirect()

        elif url.path == "/delete":
            data = parse_qs(url.query)

            domain = data.get("domain", [""])[0]

            if domain:
                remove_domain(domain)

            self.redirect()

        else:
            self.send_error(404)

    def home(self):
        rows = ""

        for domain, ip in domains.items():
            rows += f"""
            <tr>
                <td>{domain}</td>
                <td>{ip}</td>
                <td>
                    <a href="/delete?domain={domain}">
                        🗑️ Sil
                    </a>
                </td>
            </tr>
            """

        html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>EdixexSMP Panel</title>

<style>
body {{
    font-family: Arial;
    background: #111;
    color: white;
    padding: 40px;
}}

.container {{
    max-width: 800px;
    margin: auto;
}}

input {{
    padding: 10px;
    margin: 5px;
}}

button {{
    padding: 10px 20px;
    cursor: pointer;
}}

table {{
    width: 100%;
    margin-top: 30px;
    border-collapse: collapse;
}}

td, th {{
    padding: 12px;
    border-bottom: 1px solid #444;
}}
</style>

</head>

<body>

<div class="container">

<h1>🚀 EdixexSMP</h1>

<h2>Domain Yönetimi</h2>

<form action="/add">

<input
    name="domain"
    placeholder="test.edixexsmp"
    required
>

<input
    name="ip"
    placeholder="127.0.0.1"
    required
>

<button type="submit">
DOMAIN EKLE
</button>

</form>

<table>

<tr>
<th>Domain</th>
<th>IP</th>
<th>İşlem</th>
</tr>

{rows}

</table>

</div>

</body>
</html>
"""

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )
        self.end_headers()

        self.wfile.write(html.encode("utf-8"))

    def redirect(self):
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()


server = HTTPServer((HOST, PORT), Panel)

print("🚀 EdixexSMP Web Paneli çalışıyor!")
print("http://127.0.0.1:8081")

server.serve_forever()