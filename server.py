from dnslib import DNSRecord, QTYPE, RR, A
from socketserver import UDPServer, BaseRequestHandler

# Ayarlar
SERVER_IP = "127.0.0.1"
PORT = 5354

# Kullanacağımız adresler
DOMAINS = {
    "edixexsmp": SERVER_IP,
    "www.edixexsmp": SERVER_IP,
    "play.edixexsmp": SERVER_IP,
}


class DNSHandler(BaseRequestHandler):
    def handle(self):
        data, sock = self.request

        request = DNSRecord.parse(data)
        reply = request.reply()

        for question in request.questions:
            name = str(question.qname).rstrip(".").lower()

            if name in DOMAINS:
                reply.add_answer(
                    RR(
                        name,
                        QTYPE.A,
                        rdata=A(DOMAINS[name]),
                        ttl=60
                    )
                )

        sock.sendto(reply.pack(), self.client_address)


print("🚀 EdixexSMP DNS sistemi çalışıyor!")
print()
print("edixexsmp       →", SERVER_IP)
print("www.edixexsmp   →", SERVER_IP)
print("play.edixexsmp  →", SERVER_IP)
print()
print("DNS portu:", PORT)

server = UDPServer(("0.0.0.0", PORT), DNSHandler)
server.serve_forever()