from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Edixex Domains çalışıyor!"

@app.route("/health")
def health():
    return "OK"