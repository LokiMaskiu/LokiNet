from flask import Flask, render_template, request, redirect, session
import json
import os

app = Flask(__name__)

app.secret_key = "lokinet_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOSYA = os.path.join(BASE_DIR, "veritabani.json")

# ---------------------------------------------------
# VERİTABANI OLUŞTUR
# ---------------------------------------------------

if os.path.exists(DOSYA):

    with open(DOSYA, "r", encoding="utf-8") as f:
        kullanicilar = json.load(f)

else:

    kullanicilar = {}

    with open(DOSYA, "w", encoding="utf-8") as f:
        json.dump(kullanicilar, f)

# ---------------------------------------------------
# KAYDET
# ---------------------------------------------------

def kaydet():

    with open(DOSYA, "w", encoding="utf-8") as f:

        json.dump(
            kullanicilar,
            f,
            indent=4,
            ensure_ascii=False
        )

# ---------------------------------------------------
# ANA SAYFA
# ---------------------------------------------------

@app.route("/")
def index():

    kullanici = None

    if "kullanici" in session:

        kullanici = session["kullanici"]

    return render_template(
        "index.html",
        kullanici=kullanici
    )

# ---------------------------------------------------
# KAYIT OL
# ---------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    hata = ""

    if request.method == "POST":

        kullanici = request.form.get("kullanici")
        sifre = request.form.get("sifre")

        if kullanici in kullanicilar:

            hata = "Bu kullanıcı zaten var"

        else:

            kullanicilar[kullanici] = sifre

            kaydet()

            return redirect("/login")

    return render_template(
        "register.html",
        hata=hata
    )

# ---------------------------------------------------
# GİRİŞ YAP
# ---------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    hata = ""

    if request.method == "POST":

        kullanici = request.form.get("kullanici")
        sifre = request.form.get("sifre")

        if kullanici in kullanicilar:

            if kullanicilar[kullanici] == sifre:

                session["kullanici"] = kullanici

                return redirect("/panel")

            else:

                hata = "Şifre yanlış"

        else:

            hata = "Kullanıcı bulunamadı"

    return render_template(
        "login.html",
        hata=hata
    )

# ---------------------------------------------------
# PANEL
# ---------------------------------------------------

@app.route("/panel")
def panel():

    if "kullanici" in session:

        return render_template(
            "panel.html",
            kullanici=session["kullanici"]
        )

    return redirect("/login")

# ---------------------------------------------------
# ÇIKIŞ YAP
# ---------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# ---------------------------------------------------
# HESAP SİL
# ---------------------------------------------------

@app.route("/delete/<kullanici>")
def delete(kullanici):

    if kullanici in kullanicilar:

        del kullanicilar[kullanici]

        kaydet()

    session.clear()

    return redirect("/")

# ---------------------------------------------------
# ÇALIŞTIR
# ---------------------------------------------------

if __name__ == "__main__":

    app.run(debug=True)