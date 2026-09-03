domains = {
    "edixexsmp": "127.0.0.1",
    "www.edixexsmp": "127.0.0.1",
    "api.edixexsmp": "127.0.0.1",
    "auth.edixexsmp": "127.0.0.1"
}


def resolve(domain):
    return domains.get(domain)


def add_domain(domain, ip):
    domains[domain] = ip


def remove_domain(domain):
    if domain in domains:
        del domains[domain]