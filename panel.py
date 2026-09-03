from domains import domains, add_domain, remove_domain

print("================================")
print("     🚀 EDIXEXSMP DOMAIN PANEL")
print("================================")

while True:
    print()
    print("1 - Domainleri göster")
    print("2 - Domain ekle")
    print("3 - Domain sil")
    print("4 - Çıkış")

    secim = input("Seçim: ")

    if secim == "1":
        print("\n📋 Domainler:")
        for domain, ip in domains.items():
            print(f"  {domain} → {ip}")

    elif secim == "2":
        domain = input("Domain: ")
        ip = input("IP: ")

        add_domain(domain, ip)

        print(f"✅ {domain} eklendi!")

    elif secim == "3":
        domain = input("Silinecek domain: ")

        remove_domain(domain)

        print(f"🗑️ {domain} silindi!")

    elif secim == "4":
        print("👋 Panel kapatıldı.")
        break

    else:
        print("❌ Geçersiz seçim!")