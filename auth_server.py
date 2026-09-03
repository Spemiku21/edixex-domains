from flask import Flask, render_template_string, request, session, redirect
from google.oauth2 import id_token
from google.auth.transport import requests
from domains import domains, add_domain, remove_domain
import uuid

app = Flask(__name__)
app.secret_key = "edixex-secret-key"

GOOGLE_CLIENT_ID = "350915741406-hq2cmc47cs3m3u99s0lllds7mt865rk8.apps.googleusercontent.com"

DOMAIN_PRICES = {
    "com": 129.99,
    "net": 99.99,
    "org": 89.99
}

carts = {}
user_domains = {}
orders = {}


# =========================================================
# LOGIN
# =========================================================

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Edixex Domains</title>

<script src="https://accounts.google.com/gsi/client" async defer></script>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #09090d;
    color: white;
    font-family: Arial;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}

.box {
    width: 400px;
    padding: 45px;
    background: #15151d;
    border-radius: 20px;
    text-align: center;
}

.logo {
    font-size: 45px;
}

p {
    color: #999;
}

.google {
    margin-top: 30px;
}
</style>
</head>

<body>

<div class="box">

<div class="logo">🚀</div>

<h1>Edixex Domains</h1>

<p>Domainlerini yönetmek için giriş yap</p>

<div
    id="g_id_onload"
    data-client_id="{{ client_id }}"
    data-callback="handleCredentialResponse">
</div>

<div
    class="g_id_signin"
    data-type="standard"
    data-size="large"
    data-theme="filled_black">
</div>

</div>

<script>
function handleCredentialResponse(response) {

    fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            credential: response.credential
        })
    })

    .then(response => response.json())

    .then(data => {

        if (data.success) {
            window.location.href = "/panel";
        } else {
            alert("Google girişi başarısız!");
        }

    });
}
</script>

</body>
</html>
"""


# =========================================================
# PANEL
# =========================================================

PANEL_HTML = """
<!DOCTYPE html>
<html>
<head>

<meta charset="UTF-8">
<title>Edixex Domains</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #0b0b10;
    color: white;
    font-family: Arial;
}

.sidebar {
    position: fixed;
    left: 0;
    top: 0;
    width: 240px;
    height: 100vh;
    background: #111118;
    padding: 25px;
}

.logo {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 40px;
}

.menu {
    display: block;
    padding: 14px;
    margin-bottom: 8px;
    color: #aaa;
    text-decoration: none;
    border-radius: 10px;
}

.menu:hover {
    background: #1d1d28;
    color: white;
}

.main {
    margin-left: 240px;
    padding: 40px;
}

.top {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.user {
    background: #15151d;
    padding: 12px 18px;
    border-radius: 10px;
    color: #bbb;
}

.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-top: 30px;
}

.card {
    background: #15151d;
    padding: 25px;
    border-radius: 15px;
}

.number {
    font-size: 30px;
    font-weight: bold;
}

.panel {
    background: #15151d;
    margin-top: 30px;
    padding: 25px;
    border-radius: 15px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

th,
td {
    padding: 14px;
    text-align: left;
    border-bottom: 1px solid #292933;
}

.delete {
    color: #ff5c5c;
    text-decoration: none;
}

</style>
</head>

<body>

<div class="sidebar">

<div class="logo">
🚀 Edixex
</div>

<a class="menu" href="/panel">
🏠 Kontrol Paneli
</a>

<a class="menu" href="/shop">
🛒 Domain Mağazası
</a>

<a class="menu" href="/cart">
🛍️ Sepet
</a>

<a class="menu" href="/domains">
🌐 Domainlerim
</a>

<a class="menu" href="/logout">
🚪 Çıkış Yap
</a>

</div>


<div class="main">

<div class="top">

<div>

<h1>Kontrol Paneli</h1>

<p style="color:#888;">
Edixex Domains yönetim merkezi
</p>

</div>

<div class="user">
👤 {{ name }}
</div>

</div>


<div class="cards">

<div class="card">

<h3>🌐 Domainler</h3>

<div class="number">
{{ domain_count }}
</div>

</div>


<div class="card">

<h3>🛒 Sepet</h3>

<div class="number">
{{ cart_count }}
</div>

</div>


<div class="card">

<h3>⚡ Sistem</h3>

<div class="number">
Online
</div>

</div>

</div>


<div class="panel">

<h2>🌐 Domainlerim</h2>

{% if domains %}

<table>

<tr>
<th>Domain</th>
<th>IP</th>
<th>İşlem</th>
</tr>

{% for domain, ip in domains.items() %}

<tr>

<td>{{ domain }}</td>

<td>{{ ip }}</td>

<td>
<a class="delete"
href="/delete?domain={{ domain }}">
Sil
</a>
</td>

</tr>

{% endfor %}

</table>

{% else %}

<p style="color:#888;">
Henüz domain satın almadın.
</p>

{% endif %}

</div>

</div>

</body>
</html>
"""


# =========================================================
# SHOP
# =========================================================

SHOP_HTML = """
<!DOCTYPE html>
<html>

<head>

<meta charset="UTF-8">

<title>Edixex Domain Mağazası</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #0b0b10;
    color: white;
    font-family: Arial;
}

.container {
    max-width: 1000px;
    margin: auto;
    padding: 50px;
}

h1 {
    font-size: 35px;
}

.search {
    display: flex;
    gap: 10px;
    margin-top: 30px;
}

.search input {
    flex: 1;
    padding: 16px;
    border-radius: 10px;
    border: 1px solid #333;
    background: #15151d;
    color: white;
    font-size: 16px;
}

.search select {
    padding: 16px;
    border-radius: 10px;
    border: 1px solid #333;
    background: #15151d;
    color: white;
}

.search button {
    padding: 16px 25px;
    border: none;
    border-radius: 10px;
    background: #5865f2;
    color: white;
    cursor: pointer;
    font-size: 16px;
}

.result {
    margin-top: 25px;
    padding: 20px;
    background: #15151d;
    border-radius: 15px;
}

.available {
    color: #45e084;
}

.unavailable {
    color: #ff5c5c;
}

.shop {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 20px;
    margin-top: 30px;
}

.card {
    background: #15151d;
    border: 1px solid #292933;
    padding: 30px;
    border-radius: 18px;
}

.domain {
    font-size: 25px;
    font-weight: bold;
}

.price {
    font-size: 30px;
    font-weight: bold;
    margin: 20px 0;
}

.back {
    display: inline-block;
    margin-top: 30px;
    color: #aaa;
    text-decoration: none;
}

.buy {
    display: block;
    background: #5865f2;
    color: white;
    text-decoration: none;
    padding: 13px;
    text-align: center;
    border-radius: 10px;
}

.buy:hover {
    background: #4752c4;
}

</style>
</head>

<body>

<div class="container">

<h1>🛒 Domain Mağazası</h1>

<p style="color:#888;">
Edixex Domains ile kendi domainini bul.
</p>


<form class="search" action="/search" method="get">

<input
    type="text"
    name="domain"
    placeholder="örneğin: kayahost"
    required
>

<select name="extension">

<option value="com">.com</option>
<option value="net">.net</option>
<option value="org">.org</option>

</select>

<button type="submit">
🔍 Ara
</button>

</form>


{% if result %}

<div class="result">

{% if available %}

<h2 class="available">
✅ {{ result }} müsait!
</h2>

<p>
1 yıllık fiyat:
<strong>{{ "%.2f"|format(price) }} TL</strong>
</p>

<a class="buy"
href="/add-cart?domain={{ result }}">
🛒 Sepete Ekle
</a>

{% else %}

<h2 class="unavailable">
❌ {{ result }} müsait değil
</h2>

{% endif %}

</div>

{% endif %}


<h2 style="margin-top:50px;">
Domain Uzantıları
</h2>


<div class="shop">

{% for extension, price in prices.items() %}

<div class="card">

<div class="domain">
.{{ extension }}
</div>

<div class="price">
{{ "%.2f"|format(price) }} TL
</div>

<p style="color:#888;">
1 yıllık domain
</p>

</div>

{% endfor %}

</div>


<a class="back" href="/panel">
← Kontrol Paneline Dön
</a>

</div>

</body>
</html>
"""


# =========================================================
# CART
# =========================================================

CART_HTML = """
<!DOCTYPE html>
<html>

<head>

<meta charset="UTF-8">

<title>Edixex Sepet</title>

<style>

body {
    margin: 0;
    background: #0b0b10;
    color: white;
    font-family: Arial;
}

.container {
    max-width: 900px;
    margin: auto;
    padding: 50px;
}

.cart {
    background: #15151d;
    padding: 25px;
    border-radius: 15px;
}

.item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 18px;
    border-bottom: 1px solid #292933;
}

.domain {
    font-size: 20px;
    font-weight: bold;
}

.price {
    font-weight: bold;
}

.remove {
    color: #ff5c5c;
    text-decoration: none;
}

.total {
    font-size: 28px;
    font-weight: bold;
    margin-top: 25px;
}

.checkout {
    display: inline-block;
    margin-top: 25px;
    padding: 14px 25px;
    background: #5865f2;
    color: white;
    text-decoration: none;
    border-radius: 10px;
}

.back {
    display: block;
    margin-top: 25px;
    color: #aaa;
}

</style>
</head>

<body>

<div class="container">

<h1>🛍️ Sepetim</h1>

<div class="cart">

{% if items %}

{% for item in items %}

<div class="item">

<div>

<div class="domain">
{{ item["domain"] }}
</div>

<div style="color:#888;">
1 yıl
</div>

</div>

<div>

<span class="price">
{{ "%.2f"|format(item["price"]) }} TL
</span>

&nbsp;

<a class="remove"
href="/remove-cart?domain={{ item['domain'] }}">
Sil
</a>

</div>

</div>

{% endfor %}


<div class="total">
Toplam: {{ "%.2f"|format(total) }} TL
</div>


<a class="checkout" href="/checkout">
💳 Ödeme Sayfasına Geç
</a>


{% else %}

<p style="color:#888;">
Sepetiniz boş.
</p>

{% endif %}

</div>


<a class="back" href="/shop">
← Mağazaya dön
</a>

</div>

</body>
</html>
"""


# =========================================================
# PAYMENT
# =========================================================

PAYMENT_HTML = """
<!DOCTYPE html>
<html>

<head>

<meta charset="UTF-8">

<title>Edixex Ödeme</title>

<style>

body {
    margin: 0;
    background: #0b0b10;
    color: white;
    font-family: Arial;
}

.box {
    width: 500px;
    max-width: 90%;
    margin: 70px auto;
    background: #15151d;
    padding: 35px;
    border-radius: 20px;
}

h1 {
    text-align: center;
}

.notice {
    background: #222238;
    padding: 18px;
    border-radius: 12px;
    color: #aaa;
    margin: 25px 0;
}

.order {
    background: #0f0f16;
    padding: 20px;
    border-radius: 12px;
}

.item {
    display: flex;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid #292933;
}

.total {
    text-align: right;
    font-size: 27px;
    font-weight: bold;
    margin-top: 20px;
}

.pay {
    width: 100%;
    margin-top: 25px;
    padding: 16px;
    border: none;
    border-radius: 10px;
    background: #45e084;
    color: #061008;
    font-size: 17px;
    font-weight: bold;
    cursor: pointer;
}

.pay:hover {
    background: #35c970;
}

.back {
    display: block;
    text-align: center;
    margin-top: 20px;
    color: #aaa;
    text-decoration: none;
}

</style>
</head>

<body>

<div class="box">

<h1>💳 Ödeme</h1>

<div class="notice">

🧪 <strong>TEST ÖDEME</strong>

<br><br>

Bu ödeme sistemi test modundadır.

Gerçek para çekilmez.

</div>


<div class="order">

{% for item in items %}

<div class="item">

<span>
{{ item["domain"] }}
</span>

<strong>
{{ "%.2f"|format(item["price"]) }} TL
</strong>

</div>

{% endfor %}


<div class="total">

Toplam:
{{ "%.2f"|format(total) }} TL

</div>

</div>


<form action="/pay" method="post">

<button class="pay" type="submit">

💳 Test Ödemesini Yap

</button>

</form>


<a class="back" href="/cart">
← Sepete Dön
</a>

</div>

</body>
</html>
"""


# =========================================================
# SUCCESS
# =========================================================

SUCCESS_HTML = """
<!DOCTYPE html>
<html>

<head>

<meta charset="UTF-8">

<title>Edixex - Ödeme Başarılı</title>

<style>

body {
    margin: 0;
    background: #0b0b10;
    color: white;
    font-family: Arial;
}

.box {
    width: 500px;
    max-width: 90%;
    margin: 100px auto;
    background: #15151d;
    padding: 45px;
    border-radius: 20px;
    text-align: center;
}

.icon {
    font-size: 70px;
}

h1 {
    color: #45e084;
}

p {
    color: #aaa;
}

.order {
    margin-top: 20px;
    padding: 15px;
    background: #0f0f16;
    border-radius: 10px;
}

.button {
    display: block;
    margin-top: 30px;
    padding: 15px;
    background: #5865f2;
    color: white;
    text-decoration: none;
    border-radius: 10px;
    font-weight: bold;
}

</style>
</head>

<body>

<div class="box">

<div class="icon">
✅
</div>

<h1>Ödeme Başarılı!</h1>

<p>
Satın alma işlemin tamamlandı.
</p>

<div class="order">

Sipariş No:

<strong>
{{ order_id }}
</strong>

</div>

<p>
Domainlerin hesabına teslim edildi.
</p>

<a class="button" href="/panel">
🌐 Domainlerime Git
</a>

</div>

</body>
</html>
"""


# =========================================================
# ANA SAYFA
# =========================================================

@app.route("/")
def home():

    if "user" in session:
        return redirect("/panel")

    return render_template_string(
        LOGIN_HTML,
        client_id=GOOGLE_CLIENT_ID
    )


# =========================================================
# GOOGLE LOGIN
# =========================================================

@app.route("/login", methods=["POST"])
def login():

    try:

        data = request.get_json()

        credential = data["credential"]

        user = id_token.verify_oauth2_token(
            credential,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        google_id = user["sub"]

        session["user"] = {
            "google_id": google_id,
            "name": user.get("name", "Kullanıcı"),
            "email": user.get("email", "")
        }

        if google_id not in carts:
            carts[google_id] = []

        if google_id not in user_domains:
            user_domains[google_id] = {}

        print("✅ Giriş:", user.get("email"))

        return {
            "success": True
        }

    except Exception as e:

        print("❌ Giriş hatası:", e)

        return {
            "success": False
        }


# =========================================================
# PANEL
# =========================================================

@app.route("/panel")
def panel():

    if "user" not in session:
        return redirect("/")

    user = session["user"]

    google_id = user["google_id"]

    my_domains = user_domains.get(
        google_id,
        {}
    )

    my_cart = carts.get(
        google_id,
        []
    )

    return render_template_string(
        PANEL_HTML,
        name=user["name"],
        domains=my_domains,
        domain_count=len(my_domains),
        cart_count=len(my_cart)
    )


# =========================================================
# SHOP
# =========================================================

@app.route("/shop")
def shop():

    if "user" not in session:
        return redirect("/")

    return render_template_string(
        SHOP_HTML,
        prices=DOMAIN_PRICES,
        result=None,
        available=False,
        price=0
    )


# =========================================================
# DOMAIN SEARCH
# =========================================================

@app.route("/search")
def search_domain():

    if "user" not in session:
        return redirect("/")

    domain_name = request.args.get(
        "domain",
        ""
    ).strip().lower()

    extension = request.args.get(
        "extension",
        "com"
    ).lower()

    if extension not in DOMAIN_PRICES:
        extension = "com"

    domain_name = domain_name.replace(
        " ",
        ""
    ).replace(
        ".",
        ""
    )

    if not domain_name:
        return redirect("/shop")

    full_domain = domain_name + "." + extension

    google_id = session["user"]["google_id"]

    my_domains = user_domains.get(
        google_id,
        {}
    )

    available = (
        full_domain not in domains
        and full_domain not in my_domains
    )

    price = DOMAIN_PRICES[extension]

    return render_template_string(
        SHOP_HTML,
        prices=DOMAIN_PRICES,
        result=full_domain,
        available=available,
        price=price
    )


# =========================================================
# ADD CART
# =========================================================

@app.route("/add-cart")
def add_cart():

    if "user" not in session:
        return redirect("/")

    domain = request.args.get(
        "domain",
        ""
    ).strip().lower()

    if not domain:
        return redirect("/shop")

    extension = domain.split(".")[-1]

    if extension not in DOMAIN_PRICES:
        return redirect("/shop")

    if domain in domains:
        return redirect("/shop")

    google_id = session["user"]["google_id"]

    if google_id not in carts:
        carts[google_id] = []

    already_exists = any(
        item["domain"] == domain
        for item in carts[google_id]
    )

    if not already_exists:

        carts[google_id].append({
            "domain": domain,
            "price": DOMAIN_PRICES[extension],
            "years": 1
        })

    return redirect("/cart")


# =========================================================
# CART
# =========================================================

@app.route("/cart")
def cart():

    if "user" not in session:
        return redirect("/")

    google_id = session["user"]["google_id"]

    items = carts.get(
        google_id,
        []
    )

    total = sum(
        item["price"]
        for item in items
    )

    return render_template_string(
        CART_HTML,
        items=items,
        total=total
    )


# =========================================================
# REMOVE CART
# =========================================================

@app.route("/remove-cart")
def remove_cart():

    if "user" not in session:
        return redirect("/")

    domain = request.args.get("domain")

    google_id = session["user"]["google_id"]

    if google_id in carts:

        carts[google_id] = [
            item
            for item in carts[google_id]
            if item["domain"] != domain
        ]

    return redirect("/cart")


# =========================================================
# CHECKOUT
# =========================================================

@app.route("/checkout")
def checkout():

    if "user" not in session:
        return redirect("/")

    google_id = session["user"]["google_id"]

    items = carts.get(
        google_id,
        []
    )

    if not items:
        return redirect("/cart")

    total = sum(
        item["price"]
        for item in items
    )

    return render_template_string(
        PAYMENT_HTML,
        items=items,
        total=total
    )


# =========================================================
# PAY
# =========================================================

@app.route("/pay", methods=["POST"])
def pay():

    if "user" not in session:
        return redirect("/")

    google_id = session["user"]["google_id"]

    items = carts.get(
        google_id,
        []
    )

    if not items:
        return redirect("/cart")

    # Son kullanılabilirlik kontrolü

    for item in items:

        domain = item["domain"]

        if domain in domains:

            return """
            <h1>❌ Domain artık müsait değil.</h1>
            <a href="/cart">Sepete dön</a>
            """


    # TEST ÖDEME

    order_id = uuid.uuid4().hex[:10].upper()

    total = sum(
        item["price"]
        for item in items
    )


    # Sipariş kaydı

    orders[order_id] = {

        "user": google_id,

        "items": items.copy(),

        "total": total,

        "status": "paid"

    }


    # Kullanıcı domain listesi

    if google_id not in user_domains:
        user_domains[google_id] = {}


    # Domainleri teslim et

    for item in items:

        domain = item["domain"]

        user_domains[google_id][domain] = "127.0.0.1"

        add_domain(
            domain,
            "127.0.0.1"
        )


    # Sepeti temizle

    carts[google_id] = []


    return render_template_string(
        SUCCESS_HTML,
        order_id=order_id
    )


# =========================================================
# DELETE DOMAIN
# =========================================================

@app.route("/delete")
def delete_domain():

    if "user" not in session:
        return redirect("/")

    domain = request.args.get("domain")

    google_id = session["user"]["google_id"]

    if google_id in user_domains:

        if domain in user_domains[google_id]:

            del user_domains[google_id][domain]

            remove_domain(domain)

    return redirect("/panel")


# =========================================================
# DOMAINS
# =========================================================

@app.route("/domains")
def domain_page():

    if "user" not in session:
        return redirect("/")

    return redirect("/panel")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================================================
# SERVER
# =========================================================

if __name__ == "__main__":

    print("===================================")
    print("🚀 EDİXEX DOMAINS")
    print("🔐 Auth Server")
    print("🌐 http://127.0.0.1:5000")
    print("===================================")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )